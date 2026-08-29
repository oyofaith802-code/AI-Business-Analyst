from dataset_memory import (
    create_dataset_memory_table,
    save_dataset_memory,
    get_dataset_memory
)


profile = {

    "columns": [

        "customer_id",
        "sales",
        "date"

    ],

    "description":
    "Customer sales dataset"

}



create_dataset_memory_table()



save_dataset_memory(
    "sales_dataset",
    profile
)



memory = get_dataset_memory(
    "sales_dataset"
)


print(memory)