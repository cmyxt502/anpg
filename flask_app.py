from flask import Flask, request, jsonify, send_file
from flask_cors import cross_origin
import os, sys, json
import generate

app = Flask(__name__)

@app.route('/newPlate', methods=['GET'])
def newPlate():
    args = request.args
    country = args.get("country")
    plate_num = args.get("plateNum")
    side = args.get("side")
    size = args.get("size")
    badge = args.get("badge")
    generate.draw_and_validate(country, plate_num, side, size, badge)

    plate_image_path = os.path.join(sys.path[0], 'output', f'{country}_{plate_num}_{side}.png')
    plate_image_path = plate_image_path.replace(' ', '_')

    return send_file(plate_image_path)

@app.route('/loadCountries', methods=['GET'])
@cross_origin()
def loadCountries():
    """
    Load the list of countries from the config directory.
    Each country is represented by a JSON file in the 'configs' directory.
    Returns a JSON response with the list of countries and their display names.
    """
    config_dir = os.path.join(sys.path[0], 'configs')
    countries = []
    for filename in os.listdir(config_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(config_dir, filename)
            filename = filename[:-5]  # Remove the '.json' extension
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                display_name = data.get('display_name', filename)
                countries.append({'iso_code': filename, 'display_name': display_name})
    return jsonify(countries)

@app.route('/loadSizes', methods=['GET'])
@cross_origin()
def loadSizes():
    """
    Load the plate sizes from the config file for a specific country.
    Returns a JSON response with the plate sizes.
    """
    country = request.args.get("country")
    config_file = os.path.join(sys.path[0], 'configs', f'{country}.json')

    if not os.path.exists(config_file):
        return jsonify({"error": "Country configuration not found"}), 404

    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    plate_sizes_dict = config_data.get('plate_sizes', {})
    plate_sizes = [
        {
            "size_name": key,
            "display_name": value.get("display_name", key)
        }
        for key, value in plate_sizes_dict.items()
    ]
    return jsonify(plate_sizes)

@app.route('/loadBadges', methods=['GET'])
@cross_origin()
def loadBadges():
    """
    Load the plate badges from the config file for a specific country.
    Returns a JSON response with the plate badges.
    """
    country = request.args.get("country")
    config_file = os.path.join(sys.path[0], 'configs', f'{country}.json')

    if not os.path.exists(config_file):
        return jsonify({"error": "Country configuration not found"}), 404

    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    plate_badges_dict = config_data.get('badges', {})
    plate_badges = [
        {
            "badge_name": key,
            "display_name": value.get("display_name", key)
        }
        for key, value in plate_badges_dict.items()
    ]
    return jsonify(plate_badges)

if __name__ == "__main__":
    app.run(debug=True)