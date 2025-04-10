#!/bin/bash
# Script to update user_id references to aihub_user_id in routes.py

sed -i 's/user_id=current_user.id/aihub_user_id=current_user.id/g' ai_learning_hub/routes.py
sed -i 's/CompletedLesson.user_id == current_user.id/CompletedLesson.aihub_user_id == current_user.id/g' ai_learning_hub/routes.py
sed -i 's/user_id=current_user.id/aihub_user_id=current_user.id/g' ai_learning_hub/routes.py
sed -i 's/enrollment = Enrollment(user_id=current_user.id/enrollment = Enrollment(aihub_user_id=current_user.id/g' ai_learning_hub/routes.py
sed -i 's/progress = ProgressRecord(/progress = ProgressRecord(aihub_user_id=current_user.id/g' ai_learning_hub/routes.py
sed -i 's/certificate = Certificate(/certificate = Certificate(aihub_user_id=current_user.id/g' ai_learning_hub/routes.py
sed -i 's/review = Review(/review = Review(aihub_user_id=current_user.id/g' ai_learning_hub/routes.py
