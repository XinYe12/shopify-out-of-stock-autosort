import csv


def compare_products_and_separate(file1, file2, output_file):
    # Function to read products from a CSV file
    def read_products(file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return {row['Product']: row for row in reader}

    # Reading products from both files
    products1 = read_products(file1)
    products2 = read_products(file2)

    # Finding unique products
    unique_to_file1_keys = set(products1) - set(products2)
    unique_to_file2_keys = set(products2) - set(products1)

    with open(output_file, mode='w', encoding='utf-8', newline='') as file:
        writer = None

        # Write unique to file1
        if unique_to_file1_keys:
            writer = csv.DictWriter(file,
                                    fieldnames=['product'] + list(products1[next(iter(unique_to_file1_keys))].keys()))
            writer.writeheader()
            writer.writerow({'product': 'out-of-stock items that gets re-stocked'})
            writer.writerow({'product': '成功补货的产品'})
            for product in unique_to_file1_keys:
                writer.writerow(products1[product])
            writer.writerow({})  # Empty row for separation

        # Write unique to file2
        if unique_to_file2_keys:
            if not writer:
                writer = csv.DictWriter(file, fieldnames=['product'] + list(
                    products2[next(iter(unique_to_file2_keys))].keys()))
                writer.writeheader()
            writer.writerow({'product': 'new out-of-stock items'})
            writer.writerow({'product': '新出现的缺货产品'})
            for product in unique_to_file2_keys:
                writer.writerow(products2[product])


# Example usage
compare_products_and_separate('exported_data1.csv', 'exported_data2.csv', 'separated_unique_products.csv')

