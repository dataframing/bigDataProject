from pyspark.sql import SparkSession
import sys


# Establish Spark session details
spark = SparkSession.builder \
    .master("local") \
    .appName("Data Analysis CLI") \
    .getOrCreate()


def main():

    # Read input data.
    data = read_data()

    # Separate columns that are in :data from those that are not.
    valid_columns = validate_request(data.columns)

    # Analyze valid columns only.
    for column in valid_columns:
        analyze(column, data)


def read_data():
    """Reads input CSV and returns Spark DataFrame object

    :return data: Spark DataFrame representing user-provided CSV
    """

    print("Reading input file...")

    data = spark.read.csv(
        path=sys.argv[1],
        inferSchema=True,
        header=True
    )

    return data


def validate_request(data_columns):
    """Determine what user-provided columns are valid and which are invalid.

    This function takes the user command-line inputs, puts them into a set,
    and comparing that set to the set of valid columns in the data. If the user
    input any invalid columns (e.g. 'Lstitude' instead of 'Latitude'), inform
    the user. We only analyze columns that are both user-specified and valid.

    :param data_columns: columns of the Spark DataFrame object
    :return valid: set of column names as strings
    """

    # Isolate our user- and data-columns into sets.
    data_columns = set(data_columns)
    user_columns = set(sys.argv[2:])

    if ':all' in user_columns:
        return data_columns

    # Valid columns are in the intersection between the two,
    # invalid columns are in the difference from user to data columns.
    valid, invalid = user_columns.intersection(data_columns), user_columns.difference(data_columns)

    # For all invalid columns, inform the user of their invalidity.
    for column in invalid:
        print("`{}` is not a valid column --- skipping.".format(column))

    # Proceed with the analysis using only valid columns.
    return valid


# TODO base type checking -- Dave
# TODO semantic type checking -- Charlie/Dave
# TODO NULL/Invalid values (Problem Type 1) -- Charlie
# TODO Valid/Outlier values (Problem Type 2) -- Danny
def analyze(column, data):
    """Perform common analyses for a given column in our DataFrame.

    :param column: string representing column within :data
    :param data: Spark DataFrame containing user-provided CSV values
    """

    pass


def get_header():
    """Obtain the first line of a file.

    This function is primarily reserved for when a user does not specify
    columns and only runs `spark-submit faq.py <input file>.csv`. We take
    that to mean they want a nice output of what columns they *can* choose
    from, so just read the first line (which contains the column names).

    :return first_line: list of strings representing first line of comma-delimited file
    """

    # Attempt to read just the first line, split it, and return it.
    try:
        with open(sys.argv[1], 'r') as f:
            first_line = [name.strip() for name in f.readline().split(',')]
            return first_line

    # Handle auxiliary exceptions.
    except FileNotFoundError:
        print("Error: could not find file `{}`. Please try again.".format(sys.argv[1]))
        print("Exiting...")
        sys.exit(0)

    except PermissionError:
        print("Error: you do not have read-permission on file `{}`. Please try again.".format(sys.argv[1]))
        print("Exiting...")
        sys.exit(0)


def print_prompt(column_names):
    """Pretty-print column names to the user.

    This function is only called if the user runs this script as
    `spark-submit faq.py <input_file>.csv` and does not specify columns.
     We take that to mean that they want a better understanding of what
     columns they *can* choose from, so given we already read the first line
     (see get_header()), pretty-print those column names.

    :param column_names: list of strings representing column names from input CSV
    :param prompt: any particular prompt we would like to display to the user for context
    """

    # Define our prompt and print the header to our 'table'.
    prompt = "\nInput file contained the following columns:"
    print(prompt, '-' * len(prompt), sep='\n')

    # The following code for pretty-printing a matrix was sourced from:
    #   http://stackoverflow.com/questions/13214809/pretty-print-2d-python-list
    # We utilize this code to better display the available columns to the user,
    # and does not influence our project's findings or hypotheses.

    # Convert our list to a matrix (list of lists) to work properly.
    names_matrix = [column_names[i:i + 4] for i in range(0, len(column_names), 4)]

    # Do...the thing.
    lens = [max(map(len, col)) for col in zip(*names_matrix)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in names_matrix]
    print('\n'.join(table))

    # Inform the user of how they can proceed.
    print(
        "\nHence, you can now run something like:\n",
        "\t$ spark-submit faq.py {0} \'{1}\' \n".format(sys.argv[1], column_names[0]),
        "or, to run analysis on all columns:\n",
        "\t$ spark-submit faq.py {0} :all\n".format(sys.argv[1]),
        sep="\n"
    )


def cli_help():
    """Provide assistance if the user signals they need help.

    This function is only called if the user runs this script as
    `spark-submit faq.py` with no input file. If so, we inform the user
    on what actions they can take to proceed with the analysis and exit.
    """

    print(
        "\n-----------------------------------------------",
        "This file requires certain command-line inputs:",
        "-----------------------------------------------\n",

        "To get a pretty printing of your data's columns, make sure you pass in",
        "the data (with a header line containing column names, separated by commas) like so:",

            "\n\t$ spark-submit faq.py <file>.csv\n",

        "We suggest running the above if you're not sure exactly what column",
        "you'd like to analyze. Once you know what column you're looking to",
        "explore, run the following to actually analyze:",

            "\n\t$ spark-submit faq.py <file>.csv '<column name case-sensitive>'\n",

        "Note: you can also submit multiple columns to be evaluated within one run:",

            "\n\t$ spark-submit faq.py <file>.csv '<column 1>' '<column 2>' ... '<column n>'\n",
        sep="\n")

    sys.exit(0)


if __name__ == '__main__':

    if len(sys.argv) == 1:
        cli_help()

    elif len(sys.argv) == 2:
        header = get_header()
        print_prompt(header)

    else:
        main()
