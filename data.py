# Import the pandas library for data manipulation, aliasing it as pd
import pandas as pd
# Import the sys library for system-specific parameters and functions, like sys.exit
import sys
# Import various types from the typing module for type hinting, enhancing code readability and maintainability
from typing import List, Tuple, Any, Dict, Union, Optional
import traceback 
import os
# Define type aliases for clarity if needed (optional)
# RowValue = Any # Example type alias for any value in a row
# ColumnName = str # Example type alias for a column name string
# RowNumber = int # Example type alias for a row number integer

# Define the Data class
class Data:
    """
    A wrapper class for pandas DataFrames to simplify common CSV file
    interactions like reading, saving, updating, and querying data.

    Class Attributes:
        Tables (List[str]): A list keeping track of the filenames of all
                            CSV files loaded by instances of this class.
        TablesNo (int): A counter for the total number of Data objects
                        instantiated (and CSVs loaded).
    """
    # Class-level attribute to store a list of CSV file paths loaded by any instance of this class
    Tables: List[str] = []
    # Class-level attribute to count the number of Data instances created
    TablesNo: int = 0

    # The initializer method for the Data class
    def __init__(self, csv_filepath: str):
        """
        Initializes the Data object by reading a CSV file into a pandas DataFrame.

        Args:
            csv_filepath (str): The path to the CSV file to load.

        Raises:
            SystemExit: If the CSV file specified by csv_filepath cannot be found
                        or read, an error message is printed, and the program exits.
        """
        # Store the provided CSV file path as an instance attribute
        self.csv_filepath: str = csv_filepath
        # Initialize the instance attribute 'data' to None; it will hold the DataFrame
        self.data: Optional[pd.DataFrame] = None # Initialize data attribute

        # Start a try block to handle potential errors during file reading
        try:
            # Attempt to read the CSV file using pandas.read_csv into the instance's data attribute
            self.data = pd.read_csv(csv_filepath)
            # Check if the loaded DataFrame is empty
            if self.data.empty:
                # Print a warning if the file was read but resulted in an empty DataFrame
                print(f"Warning: CSV file '{self.csv_filepath}' is empty or could not be parsed correctly.")

            # Append the successfully loaded file path to the class-level list 'Tables'
            Data.Tables.append(self.csv_filepath)
            # Increment the class-level counter 'TablesNo'
            Data.TablesNo += 1

        # Handle the specific error if the file was not found at the given path
        except FileNotFoundError:
            # Print an error message indicating the file was not found
            print(f"Error: File not found at '{self.csv_filepath}'. Please check the path and try again.")
            # Exit the program with a status code of 1 (indicating an error)
            sys.exit(1) # Exit with a non-zero status code indicates an error
        # Handle the specific error if the file exists but contains no data
        except pd.errors.EmptyDataError:
             # Print an error message indicating the CSV file is empty
             print(f"Error: CSV file '{self.csv_filepath}' is empty.")
             # Exit the program with a status code of 1
             sys.exit(1)
        # Catch any other exceptions that might occur during file reading
        except Exception as e:
            # Print a general error message including the reason
            print(f"Error: Could not read CSV file '{self.csv_filepath}'. Reason: {e}")
            # Exit the program with a status code of 1
            sys.exit(1)

    # Loading Data from CSV into Class-Memory
    def _load_data(self) -> None:
        """Internal method to load data from self.csv_filepath into self.data."""
        print(f"Data:_load_data: Attempting to read '{self.csv_filepath}'")
        try:
            self.data = pd.read_csv(self.csv_filepath)
            print(f"Data:_load_data: Successfully read '{self.csv_filepath}'. Shape: {self.data.shape}")

            if self.data.empty:
                print(f"Data:_load_data: Warning - DataFrame is empty after reading '{self.csv_filepath}'.")

            expected_cols = []
            if "Heatmap.csv" in self.csv_filepath:
                 expected_cols = ['No.', 'Predictions', 'Accuracy', 'Correct', 'Closeby']
            elif "UCR.csv" in self.csv_filepath:
                 expected_cols = ['User', 'Com']
            elif "Pattern.csv" in self.csv_filepath:
                 expected_cols = ['I1', 'I2', 'I3', 'I4', 'I5', 'I6']
            elif "ComboDistributive.csv" in self.csv_filepath:
                 expected_cols = ['Combination', 'Type', 'Count']

            if expected_cols:
                missing_cols = [col for col in expected_cols if col not in self.data.columns]

                if missing_cols:
                    print(f"Data:_load_data: CRITICAL WARNING - Loaded DataFrame from '{self.csv_filepath}' is missing expected columns: {missing_cols}")
                    self.data = None
                    traceback.print_stack()
                else:
                    print(f"Data:_load_data: Columns verified for '{self.csv_filepath}'.")

        except FileNotFoundError:
            print(f"Data:_load_data: Error - File not found at '{self.csv_filepath}'.")
            self.data = None
        except pd.errors.EmptyDataError:
             print(f"Data:_load_data: Error - CSV file '{self.csv_filepath}' is empty.")
             self.data = None
        except Exception as e:
            print(f"Data:_load_data: Error - Could not read CSV file '{self.csv_filepath}'. Reason: {e}")
            self.data = None
            traceback.print_exc()

    #  Reloading
    def reload(self) -> None:
        """
        Discards the current in-memory DataFrame and attempts to re-read
        data directly from the associated CSV file (self.csv_filepath).
        Useful after the file has been modified externally or reset.
        Does not exit on error, but sets self.data to None if reload fails.
        """
        self._load_data()
        if self.data is None:
             print(f"Reload failed. In-memory data for '{self.csv_filepath}' is now None.")
        else:
             print(f"Successfully reloaded data from '{self.csv_filepath}'. Shape: {self.data.shape}")


    # Define the reset method
    def reset(self) -> None:
        """
        Resets specified instance CSV files to their default state on disk
        and then reloads the calling object's data from its associated file.
        """
        print(f"Data: reset(): Starting reset process for instance files (called on {self.csv_filepath})")

        # Define default data dictionaries
        iComDistro_dict = {
            'Combination': ['1,3,4', '1,4,3', '1,4,4', '2,3,4', '2,4,3', '2,4,4', '3,1,4', '3,2,4', '3,3,3', '3,3,4', '3,4,1', '3,4,2', '3,4,3', '3,4,4', '4,1,3', '4,1,4', '4,2,3', '4,2,4', '4,3,1', '4,3,2', '4,3,3', '4,3,4', '4,4,1', '4,4,2', '4,4,3', '4,4,4', '1,2,3', '1,2,4', '1,3,2', '1,3,3', '1,4,2', '2,1,3', '2,1,4', '2,2,3', '2,2,4', '2,3,1', '2,3,2', '2,3,3', '2,4,1', '2,4,2', '3,1,2', '3,1,3', '3,2,1', '3,2,2', '3,2,3', '3,3,1', '3,3,2', '4,1,2', '4,2,1', '4,2,2', '4,1,2', '1,1,1', '1,1,2', '1,1,3', '1,1,4', '1,2,1', '1,2,2', '1,3,1', '1,4,1', '2,1,1', '2,1,2', '2,1,3', '2,1,4', '2,2,1', '2,2,2', '3,1,1', '4,1,1'],
            'Type': ['HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW'],
            'Count': [1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 3, 1, 2, 3, 1, 3, 1, 3, 1, 2, 2, 3, 3, 1, 1, 1, 2, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 2]
        }
        iHeatmap_dict = {
            'No.': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'Predictions': [0] * 10,
            'Accuracy': [0] * 10,
            'Correct': [0] * 10,
            'Closeby': [0] * 10
        }
        iPattern_dict = {
            'I1': [], 'I2': [], 'I3': [], 'I4': [], 'I5': [], 'I6': []
        }
        iUCR_dict = {
            'User': [],
            'Com': []
        }

        # List of default dictionaries and their target file paths
        resets_to_perform = [
            (iComDistro_dict, r"datastorecsv\I_ComboDistributive.csv"),
            (iHeatmap_dict, r"datastorecsv\Instance_Heatmap.csv"),
            (iPattern_dict, r"datastorecsv\Instance_Pattern.csv"),
            (iUCR_dict, r"datastorecsv\Instance_UCR.csv"),
        ]

        # Iterate through each default dictionary and save it to its corresponding file
        for default_dict, target_filepath in resets_to_perform:
            try:
                df_to_save = pd.DataFrame(default_dict)
                print(f"Data: reset(): Writing default data to: {target_filepath}")
                df_to_save.to_csv(target_filepath, index=False)

            except ValueError as ve:
                 print(f"Data: reset(): ERROR creating DataFrame for {target_filepath}: {ve}. Check dictionary structure.")
                 traceback.print_exc()
            except Exception as e:
                 print(f"Data: reset(): ERROR writing default data to {target_filepath}: {e}")
                 traceback.print_exc()

        # After all instance files have been reset on disk,
        # reload the data specifically for *this* Data object from *its* associated file.
        print(f"Data: reset(): Instance files reset on disk. Reloading data for THIS object ({self.csv_filepath})...")
        self._load_data()

        if self.data is None:
           print(f"Data: reset(): WARNING: Reload after reset failed for {self.csv_filepath}. Instance data is None.")
        else:
           print(f"Data: reset(): Reload after reset successful for {self.csv_filepath}. Shape: {self.data.shape}. Columns: {self.data.columns.tolist()}")

    # Define the save method
    def save(self) -> None:
        """
        Saves the current state of the instance's DataFrame back to its
        associated CSV file, overwriting the original file.

        The DataFrame is saved without the pandas index column.
        """
        # Check if the instance's data attribute actually contains a DataFrame
        if self.data is not None:
            # Start a try block to handle potential errors during file saving
            try:
                # Use the DataFrame's to_csv method to save it to the instance's file path
                # index=False prevents pandas from writing the DataFrame index as a column in the CSV
                self.data.to_csv(self.csv_filepath, index=False)
            # Catch any exceptions that might occur during saving (e.g., file permissions)
            except Exception as e:
                # Print an error message including the reason
                print(f"Error: Could not save data to '{self.csv_filepath}'. Reason: {e}")
        # If the data attribute is None (no data loaded)
        else:
            # Print a warning message indicating nothing was saved
            print(f"Warning: No data loaded for '{self.csv_filepath}'. Nothing to save.")

    # Define the update_value method
    def update_value(self, row: int, column: str, value: Any) -> None:
        """
        Updates the value of a specific cell in the DataFrame and saves the changes.

        Args:
            row (int): The 1-based row number of the cell to update.
            column (str): The name of the column containing the cell to update.
            value (Any): The new value to set for the cell.

        Raises:
            KeyError: If the specified column name does not exist.
            IndexError: If the specified row number (adjusted to 0-based) is out of bounds.
        """
        # Check if data has been loaded into the instance
        if self.data is None:
            # Print an error if trying to update before loading data
            print("Error: Cannot update value, data not loaded.")
            # Exit the method
            return
        # Start a try block to handle errors during the update process
        try:
            # Convert the user-provided 1-based row number to a 0-based index for pandas
            zero_based_row_index = row - 1
            # Use the pandas .at indexer for fast, label-based setting of a single value
            # It accesses the cell at the specified 0-based row index and column name
            self.data.at[zero_based_row_index, column] = value
            # Call the save method to write the updated DataFrame back to the CSV file
            self.save()
        # Catch potential KeyError (bad column) or IndexError (bad row index) during access
        except (KeyError, IndexError) as e:
             # Print a specific error message if row or column is invalid
             print(f"Error updating value at row {row}, column '{column}': {e}. Check if row/column exists.")
        # Catch any other unexpected exceptions during the update
        except Exception as e:
             # Print a general error message
             print(f"An unexpected error occurred during update_value: {e}")

    # Define the get_value method
    def get_value(self, row: int, column: str) -> Any:
        """
        Retrieves the value of a specific cell from the DataFrame.

        Args:
            row (int): The 1-based row number of the cell.
            column (str): The name of the column containing the cell.

        Returns:
            Any: The value of the specified cell.

        Raises:
            KeyError: If the specified column name does not exist.
            IndexError: If the specified row number (adjusted to 0-based) is out of bounds.
            Returns None and prints an error if data is not loaded.
        """
        # Check if data has been loaded into the instance
        if self.data is None:
            # Print an error if trying to get value before loading data
            print("Error: Cannot get value, data not loaded.")
            # Return None as no value can be retrieved
            return None
        # Start a try block to handle errors during value retrieval
        try:
            # Convert the user-provided 1-based row number to a 0-based index
            zero_based_row_index = row - 1
            # Use the pandas .at indexer for fast, label-based retrieval of a single value
            value = self.data.at[zero_based_row_index, column]
            # Return the retrieved value
            return value
        # Catch potential KeyError (bad column) or IndexError (bad row index) during access
        except (KeyError, IndexError) as e:
             # Print a specific error message if row or column is invalid
             print(f"Error getting value at row {row}, column '{column}': {e}. Check if row/column exists.")
             # Return None to indicate failure
             return None # Return None on error
        # Catch any other unexpected exceptions during retrieval
        except Exception as e:
             # Print a general error message
             print(f"An unexpected error occurred during get_value: {e}")
             # Return None to indicate failure
             return None

    # Define the get_pos method
    def get_pos(self, value: Any) -> Tuple[List[pd.DataFrame], List[str]]:
        """
        Finds all positions (rows and columns) where a specific value occurs.

        Args:
            value (Any): The value to search for within the DataFrame.

        Returns:
            Tuple[List[pd.DataFrame], List[str]]:
                - A list where each element is a DataFrame containing the row(s)
                  from a specific column where the value was found.
                - A list of column names where the value was found.
            Returns ([], []) if data is not loaded or value is not found.
        """
        # Check if data has been loaded
        if self.data is None:
            # Print error and return empty lists if no data
            print("Error: Cannot get position, data not loaded.")
            return [], []

        # Initialize lists to store results
        found_rows_per_column: List[pd.DataFrame] = []
        found_columns: List[str] = []
        # Start try block for the search operation
        try:
            # Create a boolean DataFrame of the same shape as self.data
            # Cells are True where the original cell equals the search 'value', False otherwise
            columns_contain_value_mask = (self.data == value)
            # Find columns where *any* cell is True in the boolean mask
            # .any() checks down each column (axis=0 by default)
            # This returns a pandas Index object containing the names of matching columns
            columns_with_value = self.data.columns[columns_contain_value_mask.any()]

            # Iterate through the names of the columns found to contain the value
            for col_name in columns_with_value:
                # Filter the original DataFrame to get only the rows where the current column equals the value
                rows_in_col = self.data[self.data[col_name] == value]
                # Check if any rows were found for this column
                if not rows_in_col.empty:
                     # Append the DataFrame of matching rows for this column to the results list
                     found_rows_per_column.append(rows_in_col)
                     # Append the name of the column where the value was found
                     found_columns.append(col_name) # Store the column name

            # Return the list of DataFrames (rows per column) and the list of column names
            # Convert the pandas Index `columns_with_value` to a list for the second element if needed, but `found_columns` is already a list
            return found_rows_per_column, list(found_columns)

        # Catch any unexpected exceptions during the search
        except Exception as e:
             # Print error message
             print(f"An unexpected error occurred during get_pos for value '{value}': {e}")
             # Return empty lists on error
             return [], []

    # Define the get_row method
    def get_row(self, row: int) -> Optional[pd.Series]:
        """
        Retrieves an entire row from the DataFrame as a pandas Series.

        Args:
            row (int): The 1-based row number to retrieve.

        Returns:
            Optional[pd.Series]: The row data as a Series, or None if an error occurs
                                 (e.g., row out of bounds, data not loaded).

        Raises:
            IndexError: If the specified row number (adjusted to 0-based) is out of bounds.
                        (Handled internally, returns None)
        """
        # Check if data has been loaded
        if self.data is None:
            # Print error and return None if no data
            print("Error: Cannot get row, data not loaded.")
            return None
        # Start try block for row retrieval
        try:
            # Convert 1-based row number to 0-based index
            zero_based_row_index = row - 1
            # Use .loc[] for label-based indexing; when given an integer, it accesses the row with that index label
            # Assumes the DataFrame index is standard 0, 1, 2...
            value: pd.Series = self.data.loc[zero_based_row_index]
            # Return the retrieved row as a pandas Series
            return value
        # Catch IndexError if the 0-based index is out of the DataFrame's range
        except IndexError:
            # Print error message indicating the row number is invalid
            print(f"Error: Row number {row} is out of bounds.")
            # Return None on error
            return None
        # Catch any other unexpected exceptions
        except Exception as e:
             # Print general error message
             print(f"An unexpected error occurred during get_row for row {row}: {e}")
             # Return None on error
             return None

    # Define the get_column method
    def get_column(self, column: str) -> Optional[pd.Series]:
        """
        Retrieves an entire column from the DataFrame as a pandas Series.

        Args:
            column (str): The name of the column to retrieve.

        Returns:
            Optional[pd.Series]: The column data as a Series, or None if the column
                                 doesn't exist or data isn't loaded.

        Raises:
            KeyError: If the specified column name does not exist.
                      (Handled internally, returns None)
        """
        # Check if data has been loaded
        if self.data is None:
            # Print error and return None if no data
            print("Error: Cannot get column, data not loaded.")
            return None
        # Start try block for column retrieval
        try:
            # Access the column using dictionary-like bracket notation with the column name
            value: pd.Series = self.data[column]
            # Return the retrieved column as a pandas Series
            return value
        # Catch KeyError if the specified column name does not exist in the DataFrame
        except KeyError:
            # Print error message indicating the column was not found
            print(f"Error: Column '{column}' not found.")
            # Return None on error
            return None
        # Catch any other unexpected exceptions
        except Exception as e:
             # Print general error message
             print(f"An unexpected error occurred during get_column for column '{column}': {e}")
             # Return None on error
             return None
        
    #Define the get_rows method
    def get_rows(
        self,
        num_columns: int,
        sequence: List[Any]
    ) -> Tuple[Optional[List[List[Any]]], int]:
        """
        Filters the DataFrame to get all rows where the first `num_columns`
        columns exactly match the given sequence, and returns them as a list of lists.

        Args:
            num_columns (int): Number of leading columns to check.
            sequence (List[Any]): The sequence of values that those columns must match.

        Returns:
            Tuple[Optional[List[List[Any]]], int]:
                - A list of lists containing the matching rows, or None if an error occurred.
                - An integer giving the count of matching rows.
        """
        # Check if data is loaded
        if self.data is None:
            print("Error: data not loaded.")
            return None, 0

        # Validate inputs
        total_cols = len(self.data.columns)
        if num_columns < 1 or num_columns > total_cols:
            print(f"Error: num_columns must be between 1 and {total_cols}.")
            return None, 0
        if len(sequence) != num_columns:
            print("Error: sequence length must equal num_columns.")
            return None, 0

        try:
            # Slice out leading columns
            cols_to_check = list(self.data.columns[:num_columns])
            df_sub = self.data[cols_to_check]

            # Build mask
            mask = df_sub.apply(lambda row: row.tolist() == sequence, axis=1)

            # Filter DataFrame
            matching_df = self.data[mask]
            count = matching_df.shape[0]

            # Convert to list of lists
            result_list = matching_df.values.tolist()

            return result_list, count

        except Exception as e:
            print(f"Unexpected error: {e}")
            return None, 0


    # Define the get_columns method
    def get_columns(self, condition: Any) -> Tuple[List[str], int]:
        """
        Gets the names of all columns that contain a specific value/condition
        anywhere within them.

        Args:
            condition (Any): The value to search for within columns.

        Returns:
            Tuple[List[str], int]:
                - A list of column names containing the condition.
                - An integer count of such columns.
            Returns ([], 0) if data is not loaded.
        """
        # Check if data has been loaded
        if self.data is None:
            # Print error and return empty list and 0 count if no data
            print("Error: Cannot get columns, data not loaded.")
            return [], 0
        # Start try block for column searching
        try:
            # Create a boolean DataFrame where True indicates the condition is met
            condition_mask = (self.data == condition)
            # Find columns where '.any()' is True (checks down the column, axis=0 default)
            # Returns a pandas Index of column names where the condition exists
            columns_with_condition = self.data.columns[condition_mask.any()]
            # Convert the pandas Index object to a standard Python list of strings
            column_names_list = list(columns_with_condition)
            # Get the number of columns found (length of the list)
            count = len(column_names_list)
            # Return the list of column names and the count
            return column_names_list, count
        # Catch any other unexpected exceptions
        except Exception as e:
             # Print general error message
             print(f"An unexpected error occurred during get_columns for condition '{condition}': {e}")
             # Return empty list and 0 count
             return [], 0

    # Define the add_row method
    def add_row(self, values: Union[List[Any], Dict[str, Any]], index: Optional[int] = None) -> None:
        """
        Appends or inserts a new row to the DataFrame and saves the changes.

        Args:
            values (Union[List[Any], Dict[str, Any]]):
                The values for the new row.
                If a List, the order must match the DataFrame's column order.
                If a Dict, keys must be column names.
            index (Optional[int]):
                If None (default), the row is appended to the end (using ignore_index=True).
                If an integer, it attempts to insert the row with this index label.
        """
        # Check if data has been loaded
        if self.data is None:
            # Print error if no data
            print("Error: Cannot add row, data not loaded.")
            # Exit method
            return

        # Start try block for adding the row
        try:
            # Check if an index label was provided for insertion
            if index is None:
                # Handle appending the row to the end
                # Prepare the new row data based on whether 'values' is a dict or list
                if isinstance(values, dict):
                    # If 'values' is a dictionary, create a new single-row DataFrame from it
                    new_row_df = pd.DataFrame([values])
                elif isinstance(values, list):
                     # If 'values' is a list, check if its length matches the number of columns
                     if len(values) != len(self.data.columns):
                         # Print error if lengths don't match
                         print(f"Error: Length of values list ({len(values)}) does not match number of columns ({len(self.data.columns)}).")
                         # Exit method
                         return
                     # Create a new single-row DataFrame, specifying columns explicitly
                     new_row_df = pd.DataFrame([values], columns=self.data.columns)
                else:
                    # Print error if 'values' is neither a list nor a dict
                    print("Error: 'values' must be a List or Dict.")
                    # Exit method
                    return

                # Use pandas.concat to append the new row DataFrame to the existing one
                # ignore_index=True ensures the new row gets a sequential index label at the end
                self.data = pd.concat([self.data, new_row_df], ignore_index=True)
                # Save the modified DataFrame to the CSV file
                self.save() # Save changes

            else: # Handle insertion at a specific index label
                 # Prepare the new row data as a pandas Series
                 if isinstance(values, list):
                     # If 'values' is a list, check length
                     if len(values) != len(self.data.columns):
                         # Print error if lengths don't match
                         print(f"Error: Length of values list ({len(values)}) does not match number of columns ({len(self.data.columns)}).")
                         # Exit method
                         return
                     # Create a Series, using existing DataFrame columns as the Series index
                     new_row_series = pd.Series(values, index=self.data.columns)
                 elif isinstance(values, dict):
                     # If 'values' is a dictionary, convert it directly to a Series
                     new_row_series = pd.Series(values)
                 else:
                     # Print error if 'values' is neither list nor dict
                     print("Error: 'values' must be a List or Dict.")
                     # Exit method
                     return

                 # Use .loc[] with the specified index label to insert/overwrite the row
                 # If 'index' exists, it's overwritten; if not, it's added.
                 self.data.loc[index] = new_row_series
                 # Save the modified DataFrame
                 self.save() # Save changes

        # Catch any other unexpected exceptions during row addition
        except Exception as e:
            # Print general error message
            print(f"An unexpected error occurred during add_row: {e}")

    # Define the delete_row method
    def delete_row(self, row: int) -> None:
        """
        Deletes a row from the DataFrame based on its 1-based row number and saves.

        Args:
            row (int): The 1-based row number to delete.
        """
        # Check if data has been loaded
        if self.data is None:
            # Print error if no data
            print("Error: Cannot delete row, data not loaded.")
            # Exit method
            return
        # Start try block for row deletion
        try:
            # Convert 1-based row number to 0-based index label
            zero_based_row_index = row - 1
            # Check if the calculated 0-based index actually exists in the DataFrame's index
            if zero_based_row_index in self.data.index:
                # Use the DataFrame's .drop method to remove the row by its index label
                # Reassign the result back to self.data as .drop returns a new DataFrame by default
                self.data = self.data.drop(index=zero_based_row_index)
                # Save the modified DataFrame
                self.save() # Save changes
            else:
                 # Print error if the row number (index) doesn't exist
                 print(f"Error: Row number {row} (index {zero_based_row_index}) not found for deletion.")

        # Catch any other unexpected exceptions during row deletion
        except Exception as e:
            # Print general error message
            print(f"An unexpected error occurred during delete_row for row {row}: {e}")

    # Define the delete_column method
    def delete_column(self, column: str) -> None:
        """
        Deletes a column from the DataFrame by its name and saves the changes.

        Args:
            column (str): The name of the column to delete.
        """
        # Check if data has been loaded
        if self.data is None:
            # Print error if no data
            print("Error: Cannot delete column, data not loaded.")
            # Exit method
            return
        # Start try block for column deletion
        try:
             # Use the DataFrame's .drop method
             # Specify the column name and axis=1 to indicate column deletion
             # Reassign the result back to self.data
             self.data = self.data.drop(column, axis=1)
             # Save the modified DataFrame
             self.save() # Save changes
        # Catch KeyError if the specified column name doesn't exist
        except KeyError:
            # Print error message
            print(f"Error: Column '{column}' not found for deletion.")
        # Catch any other unexpected exceptions
        except Exception as e:
            # Print general error message
            print(f"An unexpected error occurred during delete_column for column '{column}': {e}")

    # Define the add_column method
    def add_column(self, column: str, values: Union[List[Any], pd.Series]) -> None:
        """
        Adds a new column to the DataFrame with the specified values and saves.

        Args:
            column (str): The name for the new column.
            values (Union[List[Any], pd.Series]):
                The values for the new column. Must have the same length as the
                number of rows in the DataFrame.
        """
        # Check if data has been loaded
        if self.data is None:
            # Print error if no data
            print("Error: Cannot add column, data not loaded.")
            # Exit method
            return

        # Validate that the length of the provided values matches the number of rows in the DataFrame
        # self.data.shape[0] gives the number of rows
        if len(values) != self.data.shape[0]:
            # Print error if lengths mismatch
            print(f"Error: Number of values provided ({len(values)}) does not match "
                  f"number of rows in DataFrame ({self.data.shape[0]}).")
            # Exit method
            return

        # Start try block for adding the column
        try:
            # Assign the list or Series of values directly to a new column name using bracket notation
            # Pandas automatically creates the new column
            self.data[column] = values
            # Save the modified DataFrame
            self.save() # Save changes
        # Catch any other unexpected exceptions during column addition
        except Exception as e:
            # Print general error message
            print(f"An unexpected error occurred during add_column for column '{column}': {e}")

    # Define the get_row_numbers method
    def get_row_numbers(self, condition: Any) -> List[int]:
        """
        Finds the 1-based row numbers of all rows that contain the specified
        condition/value in *any* column.

        Args:
            condition (Any): The value to search for across all cells.

        Returns:
            List[int]: A list of 1-based row numbers where the condition was found.
                       Returns an empty list if data is not loaded or condition not found.
        """
        # Check if data has been loaded
        if self.data is None:
            # Print error and return empty list if no data
            print("Error: Cannot get row numbers, data not loaded.")
            return []

        # Initialize an empty list to store the 1-based row numbers
        row_numbers: List[int] = []
        # Start try block for the search operation
        try:
            # Create a boolean DataFrame where True indicates the cell value equals the condition
            condition_mask = (self.data == condition)
            # Use .any(axis=1) to check across each row (axis=1)
            # This returns a boolean Series where the index is the DataFrame row index,
            # and the value is True if *any* cell in that row matched the condition
            rows_contain_condition: pd.Series = condition_mask.any(axis=1)

            # Iterate through the items (index, boolean_value) of the resulting Series
            for index, found in rows_contain_condition.items():
                # If the boolean value 'found' is True for this row index
                if found:
                    # Append the 1-based row number (index + 1) to the results list
                    row_numbers.append(index + 1)
            # Return the list of 1-based row numbers where the condition was found
            return row_numbers
        # Catch any other unexpected exceptions during the search
        except Exception as e:
             # Print general error message
             print(f"An unexpected error occurred during get_row_numbers for condition '{condition}': {e}")
             # Return an empty list on error
             return []
    # Define the get_column_names method
    def get_column_names(self, condition: Any) -> List[str]:
        """
        Finds the names of all columns that contain the specified condition/value
        in *any* of their cells. (Similar to get_columns but returns only names).

        Args:
            condition (Any): The value to search for across all cells.

        Returns:
            List[str]: A list of column names where the condition was found.
                       Returns an empty list if data is not loaded or condition not found.
        """
        # Check if data has been loaded
        if self.data is None:
            # Print error and return empty list if no data
            print("Error: Cannot get column names, data not loaded.")
            return []

        # Initialize an empty list to store the column names
        column_names: List[str] = []
        # Start try block for the search operation
        try:
            # Create a boolean DataFrame where True indicates the cell value equals the condition
            condition_mask = (self.data == condition)
            # Use .any() (default axis=0) to check down each column
            # This returns a boolean Series where the index is the column name,
            # and the value is True if *any* cell in that column matched the condition
            columns_contain_condition: pd.Series = condition_mask.any() # Default axis=0 (columns)

            # Iterate through the items (column_name, boolean_value) of the resulting Series
            for col_name, found in columns_contain_condition.items():
                # If the boolean value 'found' is True for this column name
                if found:
                    # Append the column name (converted to string for safety) to the results list
                    column_names.append(str(col_name)) # Add column name to the list
            # Return the list of column names where the condition was found
            return column_names
        # Catch any other unexpected exceptions during the search
        except Exception as e:
             # Print general error message
             print(f"An unexpected error occurred during get_column_names for condition '{condition}': {e}")
             # Return an empty list on error
             return []