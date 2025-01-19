import sqlite3
import logging
import os

# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker


# Function to execute a query and return a DataFrame
def execute_query(db_file, query, params):
    """
    Executes a SQL query on the specified database file using the provided query and parameters.

    Args:
        db_file (str): The path to the SQLite database file.
        query (str): The SQL query to execute.
        params (tuple or dict): The parameters to be passed to the query.

    Returns:
        pandas.DataFrame or None: The result of the query as a pandas DataFrame, or None if an error occurred.
    """
    try:
        with sqlite3.connect(db_file) as conn:
            df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        logging.error(f"Error executing query: {e}")
        return None


# Query for Liquid Limit Data with optimized JOIN order
query_ll = """
SELECT 
    pr.project_number, loc.location_name, s.sample_id, s.sample_reference, 
    l.trial, l.drops, l.tare, l.taremoist, l.taredry
FROM 
    liquidlimit l
    JOIN sample s ON l.sample_id = s.sample_id
    JOIN location loc ON s.location_id = loc.location_id
    JOIN project pr ON loc.project_id = pr.project_id
WHERE 
    pr.project_number = ?
    AND l.is_active = 1
"""

# Query for Plastic Limit Data with optimized JOIN order
query_pl = """
SELECT 
    pr.project_number, loc.location_name, s.sample_id, s.sample_reference, 
    p.trial, p.tare, p.taremoist, p.taredry
FROM 
    plasticlimit p
    JOIN sample s ON p.sample_id = s.sample_id
    JOIN location loc ON s.location_id = loc.location_id
    JOIN project pr ON loc.project_id = pr.project_id
WHERE 
    pr.project_number = ?
    AND p.is_active = 1
"""


# Configure logging
def configure_logging(project_number, log_dir=None):
    """
    Configures logging for the Atterberg Limits project.

    Args:
        project_number (str): The project number.
        log_dir (str, optional): Directory for log files. Defaults to current directory.

    Returns:
        None
    """
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"atterberg_limits_{project_number}.log")
    
    logging.basicConfig(
        filename=log_file,
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.ERROR,
    )


# Function to fetch data and create the dataframes ll_df and pl_df
def fetch_data(db_file, query, project_number):
    """
    Fetches data from the database based on the given query and project number.

    Args:
        db_file (str): Path to the SQLite database file
        query (str): The SQL query to execute.
        project_number (str): The project number to filter the data.

    Returns:
        pandas.DataFrame: The fetched data with additional calculated columns.

    Raises:
        ValueError: If no data is found for the given project number
    """
    try:
        df = execute_query(db_file, query, (project_number,))
        if df is None or df.empty:
            raise ValueError(f"No data found for project number: {project_number}")
            
        # Calculate derived columns
        df["water"] = df["taremoist"] - df["taredry"]  # Calculate the water weight
        df["soil"] = df["taredry"] - df["tare"]  # Calculate the soil weight
        df["water_content"] = df["water"] / df["soil"]  # Calculate the water content
        return df
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        raise ValueError(f"Failed to fetch data: {str(e)}")


# The following are subfunctions that are used in the main function calculation_liquid_limit
# The first subfunction is used to calculate the liquid limit
def calculate_liquid_limit(sample_df):
    try:
        x = sample_df.drops
        y = sample_df.water_content

        # Polynomial fit
        slope, intercept = np.polyfit(np.log(x), y, 1)

        x_line = np.logspace(np.log10(min(x)), np.log10(max(x)), 100)
        y_line = slope * np.log(x_line) + intercept

        liquid_limit = int(round((slope * np.log(25) + intercept) * 100, 0))

        return liquid_limit, x, y, x_line, y_line, slope, intercept

    except Exception as e:
        logging.error(
            f"Sample nonplastic or error in calculating liquid limit for sample "
            f"{sample_df['sample_reference'].iloc[0]}: {e}"
        )
        # Return a *full* 7-tuple, but with placeholders
        return (np.nan, None, None, None, None, None, None)



# The second subfunction is used to check if the drop values are within the specified ranges as outline in ASTM D4318


def check_astm_criteria(sample_df, liquid_limit):
    # Initialize flags for each range
    range_25_35 = False
    range_20_30 = False
    range_15_25 = False

    # Check to see that three trials have drop values within given ranges specified in standard
    for idx, row in sample_df.iterrows():
        trial_number = row['trial']
        drops = row['drops']
        if 25 <= drops <= 35 and not range_25_35:
            range_25_35 = True
        elif 20 <= drops <= 30 and not range_20_30:
            range_20_30 = True
        elif 15 <= drops <= 25 and not range_15_25:
            range_15_25 = True
        elif drops < 15 or drops > 35:
            logging.error(
                f"Sample {sample_df['sample_reference'].iloc[0]}, trial #{trial} is out of normal range"
            )

    # Initialize message for error logging
    message = ""
    criteria_met = range_25_35 and range_20_30 and range_15_25

    if not criteria_met:
        if not range_25_35:
            message = "Need a trial between 25 and 35 drops"
        elif not range_20_30:
            message = "Need a trial between 20 and 30 drops"
        elif not range_15_25:
            message = "Need a trial between 15 and 25 drops"

        logging.error(
            f"Sample {sample_df['sample_reference'].iloc[0]} does not meet ASTM criteria. {message}"
        )
        liquid_limit = np.nan

    return liquid_limit


# The third subfunction is used to plot the liquid limit points if liquid limit is calculated
def create_liquid_limit_plot(
    sample_df, liquid_limit, x, y, x_line, y_line, slope, intercept
):
    if not np.isnan(liquid_limit):
        location = sample_df.location_name.iloc[0]
        sample = sample_df.sample_reference.iloc[0]

        # Create plot of liquid limit points
        f, ax = plt.subplots(figsize=(12, 6))
        ax.scatter(x, y)  # Plot measured data
        ax.scatter(
            25, (slope * np.log(25) + intercept)
        )  # Plot the interpreted liquid limit value
        ax.semilogx(x_line, y_line)  # Plot the line
        ax.set_ylabel("Moisture Content")
        ax.set_xlabel("Number of Drops")
        ax.set_title("Multipoint Liquid Limit Results")
        ax.set_xscale("log")
        ax.set_yscale("linear")
        ax.set_xlim(15, 40)

        ax.xaxis.set(ticks=(15, 20, 30, 40))
        ax.tick_params(axis="both", which="both")
        ax.minorticks_on()
        ax.xaxis.set_minor_locator(
            matplotlib.ticker.LogLocator(subs="all", numticks=15)
        )

        # Customize the grid
        ax.grid(which="major", linestyle="-", linewidth="0.5", color="black")
        ax.grid(which="minor", axis="x", linestyle=":", linewidth="0.5", color="gray")

        # Add text box
        ax.annotate(
            f"Location:     {location}\nSample:       {sample}\nLiquid limit: {liquid_limit}%",
            xy=(0.8, 0.8),
            xycoords="axes fraction",
            xytext=(0.85, 0.85),
            fontsize=9,
            ha="left",
            va="bottom",
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="black", pad=0.3),
        )

        plt.savefig(
            f"liquid_limit_{location}_{sample}.png", bbox_inches="tight", pad_inches=0.3
        )


# Function to calculate the liquid limit, check if ASTM criteria are met, and plot the liquid limit points
def calculation_liquid_limit(sample_df):
    # Unpack the 7-tuple
    liquid_limit, x, y, x_line, y_line, slope, intercept = calculate_liquid_limit(sample_df)

    # Check if it's NaN or good
    liquid_limit = check_astm_criteria(sample_df, liquid_limit)

    # Plot only if we have a numeric LL
    if liquid_limit is not None and not np.isnan(liquid_limit):
        create_liquid_limit_plot(
            sample_df, liquid_limit, x, y, x_line, y_line, slope, intercept
        )

    return liquid_limit


# Function to calculate the plastic limit
def calculation_plastic_limit(sample_df):
    sample_df = sample_df.sort_values("water_content")

    # Iterate through the sorted water contents and find two trials that meet the criteria
    for i in range(len(sample_df) - 1):
        difference = abs(
            sample_df.water_content.iloc[i] - sample_df.water_content.iloc[i + 1]
        )

        if difference <= 1.4:
            plastic_limit = int(
                round(
                    (
                        sample_df.water_content.iloc[i]
                        + sample_df.water_content.iloc[i + 1]
                    )
                    / 2
                    * 100,
                    0,
                )
            )
            return plastic_limit

    # Log error if no suitable trials found
    logging.error(
        "No suitable trials found for sample {}. Consider performing additional trials unless nonplastic material.".format(
            sample_df["sample_reference"].iloc[0]
        )
    )
    return np.nan


# Modified iterate_by_sample function
def iterate_by_sample(ll_df, pl_df):
    """
    Process Atterberg limits data by sample.
    
    Args:
        ll_df (pandas.DataFrame): Liquid limit data
        pl_df (pandas.DataFrame): Plastic limit data
        
    Returns:
        pandas.DataFrame: Processed results with Atterberg limits
    """
    results = []

    # Group by location and sample
    grouped = ll_df.groupby(["location_name", "sample_reference"])

    for (location_name, sample_name), sample_group in grouped:
        try:
            # Get sample_id - should be the same for all rows in the group
            sample_id = sample_group["sample_id"].iloc[0]
            if pd.isna(sample_id):
                logging.error(f"Missing sample_id for {location_name}/{sample_name}")
                continue

            # Calculate liquid limit for this sample
            liquid_limit = calculation_liquid_limit(sample_group)

            # Get plastic limit data for this sample
            pl_sample = pl_df[
                (pl_df["location_name"] == location_name)
                & (pl_df["sample_reference"] == sample_name)
            ]

            # Calculate plastic limit
            if not pl_sample.empty:
                plastic_limit = calculation_plastic_limit(pl_sample)
                # Verify sample_id matches between LL and PL data
                pl_sample_id = pl_sample["sample_id"].iloc[0]
                if pl_sample_id != sample_id:
                    logging.warning(
                        f"Sample ID mismatch: LL={sample_id}, PL={pl_sample_id} "
                        f"for {location_name}/{sample_name}"
                    )
            else:
                plastic_limit = None

            # Calculate plasticity index and determine soil description
            if liquid_limit is not None and plastic_limit is not None:
                plasticity_index = liquid_limit - plastic_limit
                soil_description = "CH" if liquid_limit >= 50 else "CL"
            else:
                plasticity_index = None
                soil_description = "NP"

            # Create result dictionary
            result = {
                "project_number": sample_group["project_number"].iloc[0],
                "location_name": location_name,
                "sample_id": int(sample_id),  # Ensure sample_id is an integer
                "sample_reference": sample_name,
                "liquid_limit": liquid_limit if not pd.isna(liquid_limit) else None,
                "plastic_limit": plastic_limit if not pd.isna(plastic_limit) else None,
                "plasticity_index": plasticity_index if not pd.isna(plasticity_index) else None,
                "soil_description": soil_description
            }
            results.append(result)

        except Exception as e:
            logging.error(
                f"Error processing sample {sample_name} at location {location_name}: {str(e)}"
            )
            continue

    if not results:
        raise ValueError("No valid Atterberg limits data could be processed")

    return pd.DataFrame(results)


# Function to plot the atterberg limits for each sample where soil_description is not equal to "NP"
def plot_atterberg_limits(atterberg_limits):
    # For each samplename in the atterberg_limits DataFrame, plot the liquid limit and plasticity index
    for index, row in atterberg_limits.iterrows():
        if row["soil_description"] != "NP":
            location = row["location_name"]
            sample = row["sample_reference"]
            liquid_limit = row["liquid_limit"]
            plasticity_index = row["plasticity_index"]

            # Plot the sample (LL, PI)
            plt.figure()
            plt.xscale("linear")

            plt.scatter(
                liquid_limit, row["plasticity_index"], color="red", label="Sample"
            )

            # Set the maximum range value for liquid limit
            if liquid_limit < 120:
                ll_max = 120
            elif liquid_limit < 180:
                ll_max = 180
            elif liquid_limit < 240:
                ll_max = 240
            else:
                ll_max = 300

            # print(f"The maximum liquid limit x-axis value is {ll_max}")

            pi_max = ll_max / 2

            # Create a range for the x-axis (Liquid Limit)
            a_x = [0, 25.5, ll_max]

            # A-line equation
            a_y = [4, 4, (0.73 * (ll_max - 20))]

            # U-line equation
            u_x = [16, 16, ll_max]

            u_y = [0, 7, 0.9 * (ll_max - 8)]

            # Low to High plasticity dividing line construction
            ll_div = [50, 50]
            pi_div = [0, (0.9 * (50 - 8))]

            plt.plot(ll_div, pi_div, color="black")

            # Upper bound of CL-ML region
            clml_x = [0, ((7 / 0.73) + 20)]
            clml_y = [7, 7]

            plt.plot(clml_x, clml_y, color="black")

            # Plot the A-line
            plt.plot(a_x, a_y, label="A-line", color="black")

            # Plot the U-line
            plt.plot(u_x, u_y, label="U-line", color="gray", linestyle="dashed")

            # Add labels, title, grid, and legend
            plt.xlabel("Liquid Limit (LL)")
            plt.ylabel("Plasticity Index (PI)")
            plt.title("Atterberg Limits")
            # Turn on minor ticks
            plt.minorticks_on()
            plt.grid(which="major", linestyle="-", linewidth="0.5", color="gray")
            plt.grid(which="minor", axis="x", linestyle=":", linewidth="0.5", color="gray")
            plt.ylim((0, pi_max))
            plt.xlim((0, ll_max))

            # Add text box
            va = "verticalalignment"
            ha = "horizontalalignment"
            plt.text(
                2,
                58.5,
                f"Location = {location}\nSample = {sample}\nLiquid limit = {liquid_limit}\nPlasticity index = {plasticity_index}",
                fontsize=9,
                va="top",
                ha="left",
                bbox=dict(
                    boxstyle="round", facecolor="white", edgecolor="black", pad=0.3
                ),
            )

            plt.text(28, 11, "CL or OL", rotation=35, size=12, color="gray")

            plt.text(33, 3, "ML or OL", rotation=35, size=12, color="gray")

            plt.text(60, 34, "CH or OH", rotation=35, size=12, color="gray")

            plt.text(65, 26, "MH or OH", rotation=35, size=12, color="gray")

            plt.gca().set_aspect("equal")

            # Create plots directory if it doesn't exist
            plots_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plots')
            os.makedirs(plots_dir, exist_ok=True)
            
            # Save plot with full path
            plot_path = os.path.join(plots_dir, f"atterberg_limit_{location}_{sample}.png")
            plt.savefig(
                plot_path,
                bbox_inches="tight",
                pad_inches=0.3,
            )
            plt.close()  # Close the figure to free memory


def insert_or_update_atterberg_limits(df, db_path):
    """
    Insert or update Atterberg limits data in the database.
    
    Args:
        df (pandas.DataFrame): DataFrame containing Atterberg limits data
        db_path (str): Path to the SQLite database file
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # First, mark all existing records as inactive for the samples we're updating
            sample_ids = tuple(df['sample_id'].tolist())
            if len(sample_ids) == 1:
                # SQLite requires special handling for single-item tuples
                sample_ids_str = f"({sample_ids[0]})"
            else:
                sample_ids_str = str(sample_ids)
                
            cursor.execute(f"""
                UPDATE atterberglimits 
                SET is_active = 0 
                WHERE sample_id IN {sample_ids_str}
            """)

            # SQL statement for inserting new data
            insert_sql = """
            INSERT INTO atterberglimits 
                (sample_id, liquid_limit, plastic_limit, plasticity_index, 
                 soil_description, date_calculated, is_active)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
            """

            for _, row in df.iterrows():
                if pd.isna(row["sample_id"]):
                    logging.warning(f"Skipping row with missing sample_id: {row}")
                    continue
                    
                data = (
                    int(row["sample_id"]),  # Ensure sample_id is an integer
                    row["liquid_limit"] if not pd.isna(row["liquid_limit"]) else None,
                    row["plastic_limit"] if not pd.isna(row["plastic_limit"]) else None,
                    row["plasticity_index"] if not pd.isna(row["plasticity_index"]) else None,
                    row["soil_description"]
                )
                cursor.execute(insert_sql, data)

            conn.commit()
    except Exception as e:
        logging.error(f"Error inserting/updating Atterberg limits: {e}")
        raise ValueError(f"Failed to insert/update Atterberg limits: {str(e)}")


def verify_database_schema(db_file):
    """
    Verify that the database has the required tables and columns.
    
    Args:
        db_file (str): Path to the SQLite database file
        
    Raises:
        ValueError: If required tables or columns are missing
    """
    required_tables = {
        'liquidlimit': ['sample_id', 'trial', 'drops', 'tare', 'taremoist', 'taredry', 'is_active'],
        'plasticlimit': ['sample_id', 'trial', 'tare', 'taremoist', 'taredry', 'is_active'],
        'project': ['project_id', 'project_number'],
        'location': ['location_id', 'project_id', 'location_name'],
        'sample': ['sample_id', 'location_id', 'sample_reference'],
        'atterberglimits': ['sample_id', 'liquid_limit', 'plastic_limit', 'plasticity_index', 'soil_description', 'date_calculated', 'is_active']
    }
    
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            # Check each required table
            for table, columns in required_tables.items():
                if table not in existing_tables:
                    raise ValueError(f"Required table '{table}' not found in database")
                
                # Get columns for this table
                cursor.execute(f"PRAGMA table_info({table})")
                existing_columns = {row[1] for row in cursor.fetchall()}
                
                # Check each required column
                missing_columns = set(columns) - existing_columns
                if missing_columns:
                    raise ValueError(f"Table '{table}' is missing required columns: {missing_columns}")
                    
    except sqlite3.Error as e:
        raise ValueError(f"Database error: {str(e)}")


def process_atterberg_limits(db_file, project_number):
    """
    Process Atterberg limits data for a given project.
    
    Args:
        db_file (str): Path to the SQLite database file
        project_number (str): Project number to process
        
    Returns:
        pandas.DataFrame: Processed Atterberg limits data
        
    Raises:
        ValueError: If database validation fails or no data is found
    """
    try:
        # Verify database schema first
        verify_database_schema(db_file)
        
        # Configure logging
        configure_logging(project_number)
        
        # Fetch data
        ll_df = fetch_data(db_file, query_ll, project_number)
        pl_df = fetch_data(db_file, query_pl, project_number)
        
        if ll_df.empty and pl_df.empty:
            raise ValueError(f"No Atterberg limits data found for project number: {project_number}")
            
        atterberg_limits = iterate_by_sample(ll_df, pl_df)
        plot_atterberg_limits(atterberg_limits)
        insert_or_update_atterberg_limits(atterberg_limits, db_file)
        
        return atterberg_limits
    except Exception as e:
        logging.error(f"Error processing Atterberg limits: {e}")
        raise ValueError(f"Failed to process Atterberg limits: {str(e)}")
