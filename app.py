from flask import Flask, jsonify, request, abort
import pandas as pd

app = Flask(__name__)
dataset = "Global_Annual_PM2.5_GEOTIFF.csv"
# Load the data from CSV into a pandas DataFrame and set the index as the Id
data = pd.read_csv(dataset)
data.index.name = "Id"


@app.route("/getallrecords", methods=["GET"])
def get_all_records():
    """Retrieve all available records."""
    return (
        jsonify(
            {"status": "success", "data": data.reset_index().to_dict(orient="records")}
        ),
        200,
    )


@app.route("/getrecord/<int:record_Id>", methods=["GET"])
def get_record_by_Id(record_Id):
    """Fetch a specific record by Id (index)."""
    if record_Id not in data.index:
        abort(404, description="Record not found.")
    record = data.loc[record_Id]
    return jsonify({"status": "success", "data": record.to_dict()}), 200


@app.route("/addrecord", methods=["POST"])
def add_record():
    """Add a new record."""
    entry = request.get_json()
    if (
        not entry
        or "Longitude" not in entry
        or "Latitude" not in entry
        or "PM2.5_Level" not in entry
    ):
        abort(
            400,
            description="Missing required fields: Longitude, Latitude, PM2.5_Level.",
        )

    new_index = data.index.max() + 1 if len(data) > 0 else 0
    data.loc[new_index] = entry

    return (
        jsonify(
            {
                "status": "success",
                "message": "Record added successfully.",
                "data": {"Id": new_index},
            }
        ),
        201,
    )


@app.route("/updaterecord/<int:record_Id>", methods=["PUT"])
def update_record(record_Id):
    """Update an existing record by Id."""
    if record_Id not in data.index:
        abort(404, description="Record not found.")

    updates = request.get_json()
    for key, value in updates.items():
        if key in data.columns:
            data.at[record_Id, key] = value

    updated_record = data.loc[record_Id].to_dict()
    return (
        jsonify(
            {
                "status": "success",
                "message": "Record updated successfully.",
                "data": updated_record,
            }
        ),
        200,
    )


@app.route("/deleterecord/<int:record_Id>", methods=["DELETE"])
def delete_record(record_Id):
    """Delete a record by Id."""
    if record_Id not in data.index:
        abort(404, description="Record not found.")

    deleted_record = data.loc[record_Id].to_dict()
    data.drop(record_Id, inplace=True)

    return (
        jsonify(
            {
                "status": "success",
                "message": "Record deleted successfully.",
                "data": deleted_record,
            }
        ),
        200,
    )


@app.route("/records/filter", methods=["GET"])
def filter_records():
    """Filter records by latitude and longitude."""
    latitude = request.args.get("lat", type=float)
    longitude = request.args.get("long", type=float)

    filtered_data = data
    if latitude is not None:
        filtered_data = filtered_data[filtered_data["Latitude"] == latitude]
    if longitude is not None:
        filtered_data = filtered_data[filtered_data["Longitude"] == longitude]

    return (
        jsonify(
            {
                "status": "success",
                "data": filtered_data.reset_index().to_dict(orient="records"),
            }
        ),
        200,
    )


@app.route("/records/stats", methods=["GET"])
def get_stats():
    """ProvIde statistics on PM2.5 levels."""
    stats = {
        "count": int(data["PM2.5_Level"].count()),
        "average_PM2.5": float(data["PM2.5_Level"].mean()),
        "max_PM2.5": float(data["PM2.5_Level"].max()),
        "min_PM2.5": float(data["PM2.5_Level"].min()),
    }
    return jsonify({"status": "success", "data": stats}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
