# ============================================================
# TEST DATASET PROFILE STORAGE
# ============================================================

import pandas as pd

from dataset_profiles import profile_dataset

from dataset_profile_storage import (
    save_dataset_profile,
    get_dataset_profile
)


# ============================================================
# TEST DATA
# ============================================================

df = pd.DataFrame({

    "date": [
        "2026-01-01",
        "2026-01-15",
        "2026-02-01"
    ],

    "product": [
        "Laptop",
        "Phone",
        "Tablet"
    ],

    "category": [
        "Electronics",
        "Electronics",
        "Furniture"
    ],

    "revenue": [
        150000,
        120000,
        115000
    ],

    "quantity": [
        2,
        3,
        2
    ],

    "currency": [
        "USD",
        "USD",
        "USD"
    ]

})


# ============================================================
# PROFILE DATASET
# ============================================================

print(
    "📊 Profiling dataset..."
)

profile = profile_dataset(
    df
)


# ============================================================
# SAVE PROFILE
# ============================================================

print(
    "💾 Saving profile..."
)

save_dataset_profile(

    user_email="solomonenamudu@gmail.com",

    dataset_name="test_sales",

    profile=profile
)


# ============================================================
# READ PROFILE
# ============================================================

print(
    "\n🔍 Reading profile from database..."
)

saved_profile = get_dataset_profile(

    user_email="solomonenamudu@gmail.com",

    dataset_name="test_sales"
)


# ============================================================
# DISPLAY
# ============================================================

if saved_profile:

    print(
        "\n✅ PROFILE FOUND"
    )

    print(
        saved_profile
    )

else:

    print(
        "\n❌ PROFILE NOT FOUND"
    )