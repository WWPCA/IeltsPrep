#!/bin/bash
sed -i '298s/@login_required/&\ndef take_practice_test/' routes.py
sed -i '330s/@login_required/&\ndef start_complete_test/' routes.py
sed -i '378s/@login_required/&\ndef continue_complete_test/' routes.py
sed -i '410s/@login_required/&\ndef take_complete_test_section/' routes.py
sed -i '498s/@login_required/&\ndef submit_test/' routes.py
sed -i '596s/# @login_required/&\n# def speaking_assessment/' routes.py
chmod +x fix_routes.sh
./fix_routes.sh
