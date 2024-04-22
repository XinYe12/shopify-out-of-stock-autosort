# shopify-out-of-stock-autosort
This repo contains two basic python script: query.py and StockCompare.py.
The first one takes a .jsonl data of all products you have in your Shopify Store, and then process it to a visually acceptable csv file.
The second one takes two .csv files ad then compare the difference, printing the results (new out-of-stock items and successfully restocked items) to a new .csv file.
* This is the GraphQL query that I use to retrieve the products info.
```mutation {
  bulkOperationRunQuery(
    query: """
    {
      collections(first: 100) {
        edges {
          node {
            id
            title
            translations(locale: "zh-CN") {
              value
            }
            products(first: 250) {
              edges {
                node {
                  id
                  title
                  images(first: 1) {
                    edges {
                      node {
                        url
                      }
                    }
                  }
                  translations(locale: "zh-CN") {
                    value
                  }
                  variants(first: 250) {
                    edges {
                      node {
                        id
                        inventoryQuantity
                        inventoryItem {
                          updatedAt
                          unitCost {
                            amount
                            currencyCode
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
  ) {
    bulkOperation {
      id
      status
    }
    userErrors {
      field
      message
    }
  }
}
```
* and this is the GraphQL code I used to check if the current bulkOperation is done or not
```commandline
{
  currentBulkOperation {
    id
    status
    errorCode
    completedAt
    url
  }
}

```