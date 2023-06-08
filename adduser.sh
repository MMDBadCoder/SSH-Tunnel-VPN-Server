echo "#############################################"
echo "############# Create Admin User #############"
echo "#############################################"

source venv/bin/activate
python manage.py createsuperuser
