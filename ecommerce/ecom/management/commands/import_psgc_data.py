import requests
from django.core.management.base import BaseCommand
from ecom.models import Region, Province, CityMunicipality, Barangay

class Command(BaseCommand):
    help = 'Import PSGC data from https://psgc.rootscratch.com/ into local database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting import of PSGC data...')

        # Import Regions
        regions_url = 'https://psgc.rootscratch.com/regions'
        regions_response = requests.get(regions_url)
        if regions_response.status_code == 200:
            regions_data = regions_response.json()
            for region in regions_data:
                obj, created = Region.objects.update_or_create(
                    code=region['code'],
                    defaults={'name': region['name']}
                )
                if created:
                    self.stdout.write(f'Created Region: {obj.name}')
        else:
            self.stdout.write('Failed to fetch regions data')
            return

        # Import Provinces for each Region
        for region in Region.objects.all():
            provinces_url = f'https://psgc.rootscratch.com/regions/{region.code}/provinces'
            provinces_response = requests.get(provinces_url)
            if provinces_response.status_code == 200:
                provinces_data = provinces_response.json()
                for province in provinces_data:
                    obj, created = Province.objects.update_or_create(
                        code=province['code'],
                        defaults={'name': province['name'], 'region': region}
                    )
                    if created:
                        self.stdout.write(f'Created Province: {obj.name} in Region: {region.name}')
            else:
                self.stdout.write(f'Failed to fetch provinces for region {region.name}')
                return

        # Import Cities/Municipalities for each Province
        for province in Province.objects.all():
            cities_url = f'https://psgc.rootscratch.com/provinces/{province.code}/cities-municipalities'
            cities_response = requests.get(cities_url)
            if cities_response.status_code == 200:
                cities_data = cities_response.json()
                for city in cities_data:
                    obj, created = CityMunicipality.objects.update_or_create(
                        code=city['code'],
                        defaults={'name': city['name'], 'province': province}
                    )
                    if created:
                        self.stdout.write(f'Created City/Municipality: {obj.name} in Province: {province.name}')
            else:
                self.stdout.write(f'Failed to fetch cities/municipalities for province {province.name}')
                return

        # Import Barangays for each City/Municipality
        for city in CityMunicipality.objects.all():
            barangays_url = f'https://psgc.rootscratch.com/cities-municipalities/{city.code}/barangays'
            barangays_response = requests.get(barangays_url)
            if barangays_response.status_code == 200:
                barangays_data = barangays_response.json()
                for barangay in barangays_data:
                    obj, created = Barangay.objects.update_or_create(
                        code=barangay['code'],
                        defaults={'name': barangay['name'], 'city_municipality': city}
                    )
                    if created:
                        self.stdout.write(f'Created Barangay: {obj.name} in City/Municipality: {city.name}')
            else:
                self.stdout.write(f'Failed to fetch barangays for city/municipality {city.name}')
                return

        self.stdout.write('PSGC data import completed successfully.')
