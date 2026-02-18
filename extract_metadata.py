import os
import json
import segyio
import obspy
from netCDF4 import Dataset
import h5py

def extract_segy_metadata(file_path):
    metadata = {"format": "SEG-Y", "file": os.path.basename(file_path)}
    try:
        with segyio.open(file_path, "r", ignore_geometry=True) as f:
            metadata["trace_count"] = f.tracecount
            metadata["sample_count"] = f.samples.size
            metadata["sample_interval"] = f.bin[segyio.BinField.Interval]
            # Try to get text header
            text_header = segyio.tools.wrap(f.text[0])
            metadata["text_header"] = text_header[:500] + "..." if len(text_header) > 500 else text_header
    except Exception as e:
        metadata["error"] = str(e)
    return metadata

def extract_mseed_metadata(file_path):
    metadata = {"format": "MiniSEED", "file": os.path.basename(file_path)}
    try:
        st = obspy.read(file_path)
        metadata["stream_info"] = str(st)
        traces = []
        for tr in st:
            traces.append({
                "station": tr.stats.station,
                "channel": tr.stats.channel,
                "starttime": str(tr.stats.starttime),
                "endtime": str(tr.stats.endtime),
                "sampling_rate": tr.stats.sampling_rate,
                "npts": tr.stats.npts
            })
        metadata["traces"] = traces
    except Exception as e:
        metadata["error"] = str(e)
    return metadata

def extract_netcdf_metadata(file_path):
    metadata = {"format": "NetCDF", "file": os.path.basename(file_path)}
    try:
        with Dataset(file_path, "r") as ds:
            metadata["dimensions"] = {dim: len(ds.dimensions[dim]) for dim in ds.dimensions}
            metadata["variables"] = {var: list(ds.variables[var].dimensions) for var in ds.variables}
            metadata["attributes"] = {attr: str(ds.getncattr(attr)) for attr in ds.ncattrs()}
    except Exception as e:
        metadata["error"] = str(e)
    return metadata

def extract_hdf5_metadata(file_path):
    metadata = {"format": "HDF5", "file": os.path.basename(file_path)}
    try:
        with h5py.File(file_path, "r") as f:
            def get_info(name, obj):
                if isinstance(obj, h5py.Dataset):
                    items[name] = {"shape": obj.shape, "dtype": str(obj.dtype)}
                elif isinstance(obj, h5py.Group):
                    items[name] = "group"
            
            items = {}
            f.visititems(get_info)
            metadata["structure"] = items
            metadata["attributes"] = {attr: str(f.attrs[attr]) for attr in f.attrs}
    except Exception as e:
        metadata["error"] = str(e)
    return metadata

def generate_description(metadata):
    fmt = metadata["format"]
    filename = metadata["file"]
    desc = f"File: {filename} (Format: {fmt}). "
    
    if fmt == "SEG-Y":
        desc += f"Contains seismic data with {metadata.get('trace_count', 'unknown')} traces and {metadata.get('sample_count', 'unknown')} samples per trace. "
        if "text_header" in metadata:
            desc += f"Header Info: {metadata['text_header']}"
    elif fmt == "MiniSEED":
        desc += f"Seismological time-series data. Includes {len(metadata.get('traces', []))} traces. "
        if metadata.get('traces'):
            tr = metadata['traces'][0]
            desc += f"Sample Station: {tr['station']}, Channel: {tr['channel']}, Start: {tr['starttime']}, End: {tr['endtime']}."
    elif fmt == "NetCDF":
        desc += f"Multidimensional gridded data. Dimensions: {list(metadata.get('dimensions', {}).keys())}. "
        desc += f"Variables: {list(metadata.get('variables', {}).keys())}. "
        if metadata.get("attributes"):
            desc += f"Global Attributes: {metadata['attributes']}"
    elif fmt == "HDF5":
        desc += f"Hierarchical scientific data. Datasets include: { [k for k,v in metadata.get('structure', {}).items() if isinstance(v, dict)] }. "
        if metadata.get("attributes"):
            desc += f"Metadata Attributes: {metadata['attributes']}"
            
    return desc

# Geographic coordinates for known datasets
KNOWN_LOCATIONS = {
    "tohoku_earthquake_ANMO":  {"lat": 34.946, "lon": -106.457, "label": "ANMO Station, Albuquerque, NM"},
    "alaska_seismic_COLA":     {"lat": 64.874, "lon": -147.861, "label": "COLA Station, College, AK"},
    "hawaii_volcanic_POHA":    {"lat": 19.757, "lon": -155.532, "label": "POHA Station, Pohakuloa, HI"},
    "north_sea_reflection":    {"lat": 56.0,   "lon": 3.0,      "label": "North Sea, Continental Shelf"},
    "pacific_ocean_sst":       {"lat": 0.0,    "lon": 180.0,    "label": "Equatorial Pacific Ocean"},
    "bouguer_gravity_survey":  {"lat": 36.2,   "lon": -117.0,   "label": "Basin and Range Province, NV"},
}

def get_location(filename):
    """Match filename to known geographic coordinates."""
    for key, loc in KNOWN_LOCATIONS.items():
        if key in filename:
            return loc
    return {"lat": 0, "lon": 0, "label": "Unknown location"}

def main():
    data_dir = "data/raw"
    results = []
    
    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        if filename.endswith(".sgy"):
            meta = extract_segy_metadata(file_path)
        elif filename.endswith(".mseed"):
            meta = extract_mseed_metadata(file_path)
        elif filename.endswith(".nc"):
            meta = extract_netcdf_metadata(file_path)
        elif filename.endswith(".h5") or filename.endswith(".hdf5"):
            meta = extract_hdf5_metadata(file_path)
        else:
            continue
            
        description = generate_description(meta)
        location = get_location(filename)
        results.append({
            "file": filename,
            "path": file_path,
            "metadata": meta,
            "description": description,
            "location": location
        })
        
    with open("data/metadata_descriptions.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"Extracted metadata for {len(results)} files.")

if __name__ == "__main__":
    main()
