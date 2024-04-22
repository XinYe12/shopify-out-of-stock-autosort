import json
import csv

def load_and_process_data(file_path):
    products = {}
    variants = []

    # Load and parse the JSONL file
    with open(file_path, 'r') as file:
        for line in file:
            data = json.loads(line)
            # Store products separately for easy lookup
            if "Product/" in data['id']:
                products[data['id']] = data
            else:  # It's a product variant
                variants.append(data)

    # Link variants to products and process data
    processed_variants = []
    for variant in variants:
        parent_id = variant['__parentId']
        if parent_id in products:
            parent_product = products[parent_id]
            # Concatenate product and variant titles
            if variant['title'] != "Default Title":
                variant['title'] = parent_product['title'] + " · " + variant['title']
                # Concatenate translations for products and variants
                if parent_product.get('translations') and variant.get('translations'):
                    variant['translations'] = [{
                        "value": parent_product['translations'][0]['value'] + " · " + trans['value']
                        for trans in variant['translations']
                    }]
            else:
                variant['title'] = parent_product['title']
                variant['translations'] = parent_product.get('translations', [])

        # Format unitCost as "CURRENCYCODE $AMOUNT"
        unit_cost = variant["inventoryItem"].get("unitCost")
        if unit_cost:
            unit_cost_str = f"{unit_cost['currencyCode']} ${unit_cost['amount']}"
        else:
            unit_cost_str = "N/A"

        # Add only variants with inventory quantities <= 2
        if variant['inventoryQuantity'] <= 5:
            processed_variants.append({
                "title": variant["title"],
                "unitCost": unit_cost_str,
                "updatedAt": variant["inventoryItem"]["updatedAt"],
                "inventoryQuantity": variant["inventoryQuantity"],
                "translations": ", ".join([t['value'] for t in variant.get("translations", [])])
            })

    return processed_variants

def export_to_csv(variants, file_path):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["title", "translations", "unitCost", "updatedAt", "inventoryQuantity"])
        # Write the product variant data
        for variant in variants:
            writer.writerow([variant["title"], variant["translations"], variant["unitCost"], variant["updatedAt"],
                             variant["inventoryQuantity"]])

# Load, process, and export data
file_path = "shopify_data.jsonl"
processed_variants = load_and_process_data(file_path)
export_to_csv(processed_variants, 'processed_variants.csv')

print(f"Processed and exported {len(processed_variants)} product variants to CSV.")



