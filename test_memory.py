from memory import (
    create_memory_table,
    save_chat,
    get_previous_chats
)

# Create the memory table
create_memory_table()

# Save a chat
save_chat(
    "user1",
    "How many orders were delivered?",
    "SELECT COUNT(*) FROM orders;",
    "Your business has 96,478 delivered orders."
)

# Retrieve chat history
history = get_previous_chats("user1")

print("\nChat History:\n")

for item in history:
    print(item)