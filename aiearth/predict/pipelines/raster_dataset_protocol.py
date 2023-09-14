class RasterDatasetProtocol:
    # driver::protocol
    geoserver = ["geoserver://"]
    local = ["local://", "/"]


def resolve_uri(uri: str):
    for protocol in RasterDatasetProtocol.local:
        if uri.startswith(protocol):
            if protocol == "/":
                return (RasterDatasetProtocol.local, uri)
            else:
                return (RasterDatasetProtocol.local, uri[len(protocol) :])

    for protocol in RasterDatasetProtocol.geoserver:
        if uri.startswith(protocol):
            return (RasterDatasetProtocol.geoserver, uri[len(protocol) :])

    raise RuntimeError(f"uri protocol resolve error. uri:{uri}")
