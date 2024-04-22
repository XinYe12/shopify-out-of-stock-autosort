import json
import csv

# File paths
jsonl_file_path = 'shopify_data.jsonl'
csv_file_path = 'exported_data.csv'

# Helper function to extract company name
def get_company_name(product_title):
    parts = product_title.split(' · ')
    return parts[0].strip() if len(parts) > 1 else 'Unknown'

# Helper function to concatenate translations
def concatenate_translations(product_translations, variant_translations):
    return ", ".join(filter(None, [product_translations, variant_translations]))

# Function to process the .jsonl file and export data
def process_and_export_data(jsonl_file_path, csv_file_path):
    collection_titles = {}
    product_info = {}
    variant_info = []
    processed_variants = set()  # To track processed product variants

    # First pass: Read collections and products to build mappings
    with open(jsonl_file_path, 'r') as file:
        for line in file:
            item = json.loads(line)
            if 'id' in item and 'title' in item:
                if 'Collection' in item['id']:
                    collection_titles[item['id']] = item['title']
                elif 'id' in item and 'Product' in item['id']:
                    company_name = get_company_name(item['title'])
                    product_info[item['id']] = {
                        'collection_id': item['__parentId'],
                        'title': item['title'],
                        'company': company_name,
                        'translations': ", ".join([t['value'] for t in item.get('translations', [])])
                    }

    # Second pass: Read variants, filter by quantity, avoid duplicates, and concatenate translations
    with open(jsonl_file_path, 'r') as file:
        for line in file:
            item = json.loads(line)
            if 'id' in item and 'ProductVariant' in item['id'] and item['id'] not in processed_variants and item['inventoryQuantity'] <= 5:
                processed_variants.add(item['id'])  # Mark as processed

                product = product_info.get(item['__parentId'], {})
                collection_id = product.get('collection_id')
                collection_title = collection_titles.get(collection_id, "Unknown Collection")
                product_title = product.get('title', "Unknown Product")
                company = product.get('company', "Unknown")
                product_translations = product.get('translations', "N/A")

                variant_title = "No Variant" if item.get('title') == "Default Title" else item.get('title')
                variant_translations = ", ".join([t['value'] for t in item.get('translations', [])])
                concatenated_translations = concatenate_translations(product_translations, variant_translations)

                unit_cost = f"{item['inventoryItem']['unitCost']['amount']} {item['inventoryItem']['unitCost']['currencyCode']}" if item['inventoryItem'].get('unitCost') else "N/A"
                updated_at = item['inventoryItem']['updatedAt']
                inventory_quantity = item['inventoryQuantity']

                variant_info.append({
                    'Collection': collection_title,
                    'Company': company,
                    'Product': product_title,
                    'Variant': variant_title,
                    'Translations': concatenated_translations,
                    'Unit Cost': unit_cost,
                    'Updated At': updated_at,
                    'Inventory Quantity': inventory_quantity,
                })

    # Group by collection and company, then sort
    sorted_variants = sorted(variant_info, key=lambda x: (x['Collection'], x['Company']))

    # Export sorted data to CSV
    with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['Collection', 'Company', 'Product', 'Variant', 'Translations', 'Unit Cost', 'Updated At', 'Inventory Quantity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_variants)

    print(f"{len(sorted_variants)} product variants with quantity less or equal to 5 exported successfully to {csv_file_path}")

process_and_export_data(jsonl_file_path, csv_file_path)

