"""
Download real geophysical datasets for RAG development.

- MiniSEED: Real earthquake recordings from IRIS FDSN web services
- SEG-Y: Realistic synthetic seismic reflection profile
- NetCDF: Realistic ocean temperature grid (NOAA-style)
- HDF5: Realistic gravity survey data
"""
import os
import numpy as np

DATA_DIR = "data/raw"
os.makedirs(DATA_DIR, exist_ok=True)


def download_real_miniseed():
    """Download real seismological waveforms from IRIS FDSN."""
    from obspy.clients.fdsn import Client
    from obspy import UTCDateTime

    client = Client("IRIS")

    # 1. 2011 Tohoku Earthquake (M9.1) recorded at ANMO station, New Mexico
    print("Downloading Tohoku M9.1 earthquake recording from ANMO...")
    try:
        st1 = client.get_waveforms(
            network="IU", station="ANMO", location="00", channel="BHZ",
            starttime=UTCDateTime("2011-03-11T05:46:00"),
            endtime=UTCDateTime("2011-03-11T06:00:00")
        )
        path1 = os.path.join(DATA_DIR, "tohoku_earthquake_ANMO_BHZ.mseed")
        st1.write(path1, format="MSEED")
        print(f"  Saved: {path1} ({os.path.getsize(path1)} bytes)")
    except Exception as e:
        print(f"  Failed: {e}")

    # 2. Yellowstone microseismicity
    print("Downloading Yellowstone seismic data from YMR station...")
    try:
        st2 = client.get_waveforms(
            network="WY", station="YMR", location="01", channel="EHZ",
            starttime=UTCDateTime("2024-01-15T00:00:00"),
            endtime=UTCDateTime("2024-01-15T00:10:00")
        )
        path2 = os.path.join(DATA_DIR, "yellowstone_YMR_EHZ.mseed")
        st2.write(path2, format="MSEED")
        print(f"  Saved: {path2} ({os.path.getsize(path2)} bytes)")
    except Exception as e:
        print(f"  Failed: {e}")

    # 3. California seismic noise (ambient noise)
    print("Downloading California ambient noise from BK.BRK station...")
    try:
        st3 = client.get_waveforms(
            network="BK", station="BRK", location="00", channel="BHZ",
            starttime=UTCDateTime("2023-06-01T12:00:00"),
            endtime=UTCDateTime("2023-06-01T12:05:00")
        )
        path3 = os.path.join(DATA_DIR, "california_ambient_BRK_BHZ.mseed")
        st3.write(path3, format="MSEED")
        print(f"  Saved: {path3} ({os.path.getsize(path3)} bytes)")
    except Exception as e:
        print(f"  Failed: {e}")


def create_realistic_segy():
    """Create a realistic synthetic seismic reflection profile."""
    import segyio

    print("Creating realistic SEG-Y seismic reflection profile...")

    n_traces = 200
    n_samples = 500
    dt = 0.002  # 2ms sample interval (typical for seismic)

    # Build a realistic geological model with 5 reflectors
    reflector_depths = [80, 150, 220, 310, 400]  # in samples
    reflector_amplitudes = [0.3, -0.5, 0.8, -0.2, 0.6]

    data = np.zeros((n_traces, n_samples), dtype='float32')

    for i in range(n_traces):
        trace = np.zeros(n_samples)
        for depth, amp in zip(reflector_depths, reflector_amplitudes):
            # Add geological structure (slight dip + anticline)
            offset = int(depth + 5 * np.sin(2 * np.pi * i / 150) + 0.02 * i)
            if 0 <= offset < n_samples:
                # Ricker wavelet centered at the reflector
                f = 30  # dominant frequency 30Hz
                t = np.arange(n_samples) * dt
                t0 = offset * dt
                arg = (np.pi * f * (t - t0)) ** 2
                wavelet = amp * (1 - 2 * arg) * np.exp(-arg)
                trace += wavelet

        # Add realistic random noise
        trace += np.random.normal(0, 0.05, n_samples)
        data[i] = trace.astype('float32')

    spec = segyio.spec()
    spec.samples = range(n_samples)
    spec.tracecount = n_traces
    spec.format = 1

    path = os.path.join(DATA_DIR, "north_sea_reflection_profile.sgy")
    with segyio.create(path, spec) as f:
        for i in range(n_traces):
            f.trace[i] = data[i]
            # Set realistic trace headers
            f.header[i][segyio.TraceField.TRACE_SEQUENCE_LINE] = i + 1
            f.header[i][segyio.TraceField.FieldRecord] = 1001
            f.header[i][segyio.TraceField.TraceNumber] = i + 1
            f.header[i][segyio.TraceField.CDP] = 1000 + i
            f.header[i][segyio.TraceField.offset] = 100 + i * 25
            f.header[i][segyio.TraceField.SourceX] = 500000 + i * 12
            f.header[i][segyio.TraceField.SourceY] = 6200000
            f.header[i][segyio.TraceField.GroupX] = 500000 + i * 12 + 100 + i * 25
            f.header[i][segyio.TraceField.GroupY] = 6200000

    print(f"  Saved: {path} ({os.path.getsize(path)} bytes)")


def create_realistic_netcdf():
    """Create a realistic NetCDF ocean temperature dataset (NOAA-style)."""
    from netCDF4 import Dataset
    from datetime import datetime

    print("Creating realistic NetCDF ocean temperature dataset...")

    path = os.path.join(DATA_DIR, "pacific_ocean_sst_2023.nc")
    with Dataset(path, "w", format="NETCDF4") as ds:
        # Global attributes (mimicking NOAA products)
        ds.title = "Pacific Ocean Sea Surface Temperature Analysis"
        ds.institution = "Generated for GeoRAG demo (NOAA OISST-style)"
        ds.source = "Optimum Interpolation Sea Surface Temperature (OISST)"
        ds.Conventions = "CF-1.6"
        ds.history = f"Created {datetime.now().isoformat()} for RAG development"

        # Dimensions: monthly data over a small Pacific region
        n_time = 12  # 12 months
        n_lat = 30   # 30 degrees latitude
        n_lon = 60   # 60 degrees longitude
        n_depth = 5  # 5 depth levels

        ds.createDimension("time", n_time)
        ds.createDimension("lat", n_lat)
        ds.createDimension("lon", n_lon)
        ds.createDimension("depth", n_depth)

        # Coordinate variables
        time_var = ds.createVariable("time", "f4", ("time",))
        time_var.units = "months since 2023-01-01"
        time_var.calendar = "standard"
        time_var[:] = np.arange(n_time)

        lat_var = ds.createVariable("lat", "f4", ("lat",))
        lat_var.units = "degrees_north"
        lat_var.long_name = "Latitude"
        lat_var[:] = np.linspace(-15, 15, n_lat)

        lon_var = ds.createVariable("lon", "f4", ("lon",))
        lon_var.units = "degrees_east"
        lon_var.long_name = "Longitude"
        lon_var[:] = np.linspace(150, 210, n_lon)

        depth_var = ds.createVariable("depth", "f4", ("depth",))
        depth_var.units = "meters"
        depth_var.positive = "down"
        depth_var[:] = [0, 10, 50, 100, 200]

        # Sea Surface Temperature with realistic spatial and seasonal patterns
        sst = ds.createVariable("sst", "f4", ("time", "lat", "lon"),
                                zlib=True, complevel=4)
        sst.units = "degC"
        sst.long_name = "Sea Surface Temperature"
        sst.valid_range = [5.0, 35.0]

        lat_vals = np.linspace(-15, 15, n_lat)
        lon_vals = np.linspace(150, 210, n_lon)

        for t in range(n_time):
            seasonal = 2 * np.cos(2 * np.pi * (t - 1) / 12)
            for j, lat in enumerate(lat_vals):
                for k, lon in enumerate(lon_vals):
                    # Base temperature: warm equator, cooler at higher latitudes
                    base = 28 - 0.3 * abs(lat)
                    # Cold tongue in eastern equatorial Pacific
                    if abs(lat) < 5 and lon > 180:
                        base -= 3
                    sst[t, j, k] = base + seasonal + np.random.normal(0, 0.5)

        # Subsurface temperature
        temp_3d = ds.createVariable("temperature", "f4",
                                     ("time", "depth", "lat", "lon"),
                                     zlib=True, complevel=4)
        temp_3d.units = "degC"
        temp_3d.long_name = "Ocean Temperature Profile"

        depths = [0, 10, 50, 100, 200]
        for t in range(n_time):
            for d, depth_m in enumerate(depths):
                depth_cooling = depth_m * 0.05
                temp_3d[t, d, :, :] = sst[t, :, :] - depth_cooling + np.random.normal(0, 0.2, (n_lat, n_lon))

        # Salinity
        sal = ds.createVariable("salinity", "f4", ("time", "lat", "lon"),
                                 zlib=True, complevel=4)
        sal.units = "PSU"
        sal.long_name = "Sea Surface Salinity"
        for t in range(n_time):
            sal[t, :, :] = 35.0 + np.random.normal(0, 0.3, (n_lat, n_lon))

    print(f"  Saved: {path} ({os.path.getsize(path)} bytes)")


def create_realistic_hdf5():
    """Create a realistic HDF5 gravity survey dataset."""
    import h5py

    print("Creating realistic HDF5 gravity survey dataset...")

    path = os.path.join(DATA_DIR, "bouguer_gravity_survey.h5")
    with h5py.File(path, "w") as f:
        # Root attributes
        f.attrs["title"] = "Bouguer Gravity Anomaly Survey - Basin and Range Province"
        f.attrs["institution"] = "Generated for GeoRAG demo (USGS-style)"
        f.attrs["survey_date"] = "2023-06-15"
        f.attrs["datum"] = "WGS84"
        f.attrs["units"] = "mGal"

        # Survey grid
        n_stations = 500
        n_east = 50
        n_north = 10

        # Station coordinates (UTM-like)
        coords = f.create_group("coordinates")
        easting = np.linspace(300000, 350000, n_east)
        northing = np.linspace(4000000, 4010000, n_north)
        ee, nn = np.meshgrid(easting, northing)

        coords.create_dataset("easting", data=ee.flatten())
        coords.create_dataset("northing", data=nn.flatten())
        coords.create_dataset("elevation", data=1500 + 200 * np.random.rand(n_stations))
        coords["easting"].attrs["units"] = "meters"
        coords["northing"].attrs["units"] = "meters"
        coords["elevation"].attrs["units"] = "meters"

        # Gravity measurements
        gravity = f.create_group("gravity")

        # Observed gravity with a basin anomaly
        observed = np.zeros(n_stations)
        for i in range(n_stations):
            x = ee.flatten()[i]
            y = nn.flatten()[i]
            # Basin anomaly (negative Bouguer anomaly)
            cx, cy = 325000, 4005000
            basin = -30 * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * 5000 ** 2))
            # Regional trend
            regional = 0.001 * (x - 300000) - 0.0005 * (y - 4000000)
            observed[i] = -100 + basin + regional + np.random.normal(0, 0.5)

        gravity.create_dataset("observed_gravity", data=observed)
        gravity.create_dataset("free_air_anomaly", data=observed + 50 + np.random.normal(0, 0.3, n_stations))
        gravity.create_dataset("bouguer_anomaly", data=observed + np.random.normal(0, 0.2, n_stations))
        gravity["observed_gravity"].attrs["units"] = "mGal"
        gravity["free_air_anomaly"].attrs["units"] = "mGal"
        gravity["bouguer_anomaly"].attrs["units"] = "mGal"

        # Quality flags
        qc = f.create_group("quality")
        qc.create_dataset("measurement_error", data=np.random.uniform(0.1, 1.0, n_stations))
        qc.create_dataset("repeat_readings", data=np.random.randint(2, 6, n_stations))
        qc["measurement_error"].attrs["units"] = "mGal"

    print(f"  Saved: {path} ({os.path.getsize(path)} bytes)")


def main():
    # Remove old synthetic samples
    for old_file in ["sample.sgy", "sample.nc", "sample.h5", "test1.h5", "test.mseed"]:
        old_path = os.path.join(DATA_DIR, old_file)
        if os.path.exists(old_path):
            os.remove(old_path)
            print(f"Removed old file: {old_path}")

    download_real_miniseed()
    create_realistic_segy()
    create_realistic_netcdf()
    create_realistic_hdf5()

    print("\n--- All datasets ready ---")
    for f in sorted(os.listdir(DATA_DIR)):
        fp = os.path.join(DATA_DIR, f)
        if os.path.isfile(fp):
            print(f"  {f}: {os.path.getsize(fp):,} bytes")


if __name__ == "__main__":
    main()
