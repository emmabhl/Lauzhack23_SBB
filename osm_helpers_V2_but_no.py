from pyroutelib3 import Router # Import the router

def get_itinerary(start, destination, transport_mode='car'):
    # Initialise the router
    router = Router(transport_mode)

    # Find the start and end nodes
    start_node = router.findNode(start['latitude'], start['longitude'])
    end_node = router.findNode(destination['latitude'], destination['longitude'])

    # Find the route - a list of OSM nodes
    status, route = router.doRoute(start_node, end_node)
    return route, router

    if status == 'success':
        routeLatLons = list(map(router.nodeLatLon, route)) 
    #for i in range(len(route)):
    #    route_latitudes.append(router.nodeLatLon(route[i])[0])
    #    route_longitudes.append(router.nodeLatLon(route[i])[1])

    # Return the route
    return routeLatLons

