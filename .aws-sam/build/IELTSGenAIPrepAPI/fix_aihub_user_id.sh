#!/bin/bash

# Fix multiple instances of aihub_aihub_aihub_user_id
sed -i 's/aihub_aihub_aihub_user_id/aihub_user_id/g' ai_learning_hub/routes.py

# Fix instances of aihub_aihub_user_id
sed -i 's/aihub_aihub_user_id/aihub_user_id/g' ai_learning_hub/routes.py

# Check if successful
grep -n "aihub_" ai_learning_hub/routes.py
