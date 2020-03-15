import url_util
import make_model_fetcher
import csv
import argparse

parser = argparse.ArgumentParser(description='Scrape and import Kelley Blue Book data for a given year to a CSV file.')
parser.add_argument('year', type=int, help='Year to get Vehicle data for.')

args = parser.parse_args()
year = args.year

f = open('Kelley_Blue_Book_Cars_{:d}.csv'.format(year), 'w')
headers = ['Make', 'Model', 'Year', 'Style', 'Out of Pocket Expenses', 'Loss of Value', '5 Year Cost to Own', 'Fuel Economy', 'Fuel Type', 'Basic Warranty', 'Max Seating', 'Horsepower', 'Cargo Space', 'Engine', 'Torque', 'Bore x Stroke', 'Compression Ratio', 'Fuel Induction', 'Valve Train', 'Valves Per Cylinder', 'Total Number Valves', 'Transmission', 'Drivetrain', 'Transfer Case', 'Fuel Capacity', 'Wheel Base', 'Overall Length', 'Width with Mirrors', 'Width without Mirrors', 'Height', 'Curb Weight', 'Tires / Wheel Size', 'Rear Tires / Wheel Size', 'Turning Diameter', 'Standard Axle Ratio', 'Minimum Ground Clearance', 'Maximum Ground Clearance', 'Maximum GVWR', 'Maximum Towing', 'Payload Base Capacity', 'Head Room: Front', 'Head Room: Rear', 'Leg Room: Front', 'Leg Room: Rear', 'Shoulder Room: Front', 'Shoulder Room: Rear', 'EPA Passenger', 'EPA Trunk or Cargo', 'EPA Total Interior']
writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
writer.writeheader()

makes_list = make_model_fetcher.get_kbb_makes()

for make in makes_list:
    print("Getting models for {}".format(make.name))
    models_list = make_model_fetcher.get_kbb_models_per_make(make)

    for model in models_list:
        print("Getting styles for {} {}".format(make.name, model.name))
        make_name = make.name.lower().replace(" ", "-")
        model_name = model.name.lower().replace(" ", "-")
        try:
            style_urls = url_util.fetch_style_urls_for_model(make_name, model_name, year)
            print(style_urls)
        except Exception:
            print("Exception while getting Styles for {} {}".format(make_name, model_name))
            continue

        for style_url in style_urls:
            vehicle_id = url_util.extract_vehicleid_from_style_url(style_url)
            style_name = url_util.extract_style_name_from_style_url(style_url)

            print("Getting Vehicle information for {} {} {} {}".format(make.name, model.name, style_name, vehicle_id))

            cto_dict = url_util.fetch_cto_values_for_vehicleid(vehicle_id)

            car_dict = {}
            car_dict["Make"] = make.name
            car_dict["Model"] = model.name
            car_dict["Year"] = year
            car_dict["Style"] = style_name

            specs_dict = url_util.scrape_specs_for_vehicleid(vehicle_id)

            complete_car_spec_dict = {**car_dict, **cto_dict, **specs_dict}

            print("Writing Vehicle information for {} {} {} {}".format(make.name, model.name, style_name, vehicle_id))
            writer.writerow(complete_car_spec_dict)

            #print(complete_car_spec_dict)
            #print(make_name, model_name, "2019", style_name, ' '.join(cto_dict.values()), ' '.join(specs_dict.values()))

f.close()