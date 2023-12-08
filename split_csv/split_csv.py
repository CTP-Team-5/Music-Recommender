import csv

# Open the original CSV file for reading
with open('spotify_millsongdata.csv', 'r', newline='') as csvfile:
    # Create CSV readers for the original file
    reader = csv.reader(csvfile)

    # Create two output CSV files
    output_file1 = open('output_file1.csv', 'w', newline='')
    output_file2 = open('output_file2.csv', 'w', newline='')

    # Create CSV writers for the output files
    writer1 = csv.writer(output_file1)
    writer2 = csv.writer(output_file2)

    # Define a variable to keep track of the row count
    row_count = 0

    # Split the CSV file based on a condition (for example, row count)
    for row in reader:
        if row_count < 10000:  # Split after 5000 rows
            writer1.writerow(row)
        else:
            writer2.writerow(row)
        row_count += 1

    # Close the output files
    output_file1.close()
    output_file2.close()

# Close the original CSV file
csvfile.close()
