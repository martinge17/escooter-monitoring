use m365::gps_location::GPSInfo;

#[test]
fn it_parses_gps() {
    let raw = "+CGPSINFO: 4319.736021,N,00824.498574,W,150724,162016.0,176.0,0.0,";
    let gps_info = GPSInfo::parse(raw).unwrap();

    assert_eq!(gps_info.latitude, 43.32893368333333);
    assert_eq!(gps_info.longitude, -8.408309566666667);
    assert_eq!(gps_info.altitude, 176.0);
    assert_eq!(gps_info.gps_speed, 0.0);
    //assert_eq!(gps_info.nav_angle, 0.0);

}

#[test]
fn it_parses_gps_null() {
    let raw = "+CGPSINFO: 9119.736021,N,00824.498574,W,150724,162016.0,176.0,0.0,";
    let gps_info = GPSInfo::parse(raw).unwrap();

    assert_eq!(gps_info.latitude, 0.0);
    assert_eq!(gps_info.longitude, 0.0);
    assert_eq!(gps_info.altitude, 0.0);
    assert_eq!(gps_info.gps_speed, 0.0);

}

#[test]
fn it_parses_json() {
    let raw = "+CGPSINFO: 4319.736021,N,00824.498574,W,150724,162016.0,176.0,0.0,";
    let gps_info = GPSInfo::parse(raw).unwrap();
    let json = serde_json::to_string(&gps_info).unwrap();
    assert_eq!(json, "{\"latitude\":43.32893368333333,\"longitude\":-8.408309566666667,\"altitude\":176.0,\"gps_speed\":0.0}");
}