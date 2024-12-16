import Py4GW
import PyMap
import PyPlayer

class Map:
    @staticmethod
    def map_instance():
        """Return the PyMap instance. """
        return PyMap.PyMap() 

    @staticmethod
    def IsMapReady():
        """Check if the map is ready to be handled."""
        return Map.map_instance().is_map_ready

    @staticmethod
    def IsOutpost():
        """Check if the map instance is an outpost."""
        return Map.map_instance().instance_type.GetName() == "Outpost"

    @staticmethod
    def IsExplorable():
        """Check if the map instance is explorable."""
        return Map.map_instance().instance_type.GetName() == "Explorable"

    @staticmethod
    def IsMapLoading():
        """Check if the map instance is loading."""
        return Map.map_instance().instance_type.GetName() == "Loading"

    @staticmethod
    def GetMapName(mapid=None):
        """
        Retrieve the name of a map by its ID.
        Args:
            mapid (int, optional): The ID of the map to retrieve. Defaults to the current map.
        Returns: str
        """
        if mapid is None:
            map_id = Map.GetMapID()
        else:
            map_id = mapid
        map_id_instance = PyMap.MapID(map_id)
        return map_id_instance.GetName()

    @staticmethod
    def GetMapID():
        """Retrieve the ID of the current map."""
        return Map.map_instance().map_id.ToInt()

    @staticmethod
    def Travel(map_id):
        """Travel to a map by its ID."""
        Map.map_instance().Travel(map_id)

    @staticmethod
    def TravelToDistrict(map_id, district=0, district_number=0):
        """
        Travel to a map by its ID and district.
        Args:
            map_id (int): The ID of the map to travel to.
            district (int): The district to travel to.
            district_number (int): The number of the district to travel to.
        Returns: None
        """
        Map.map_instance().Travel(map_id, district, district_number)

    @staticmethod
    def GetInstanceUptime():
        """Retrieve the uptime of the current instance."""
        return Map.map_instance().instance_time

    @staticmethod
    def GetMaxPartySize():
        """ Retrieve the maximum party size of the current map."""
        return Map.map_instance().max_party_size

    @staticmethod
    def IsInCinematic():
        """Check if the map is in a cinematic."""
        return Map.map_instance().is_in_cinematic

    @staticmethod
    def SkipCinematic():
        """ Skip the cinematic."""
        Map.map_instance().SkipCinematic()

    @staticmethod
    def HasEnterChallengeButton():
        """Check if the map has an enter challenge button."""
        return Map.map_instance().has_enter_button

    @staticmethod
    def EnterChallenge():
        """Enter the challenge."""
        Map.map_instance().EnterChallenge()

    @staticmethod
    def CancelEnterChallenge():
        """Cancel entering the challenge."""
        Map.map_instance().CancelEnterChallenge()

    @staticmethod
    def IsVanquishable():
        """Check if the map is vanquishable."""
        return Map.map_instance().is_vanquishable_area

    @staticmethod
    def GetFoesKilled():
        """
        Retrieve the number of foes killed in the current map.
        Args: None
        Returns: int
        """
        return Map.map_instance().foes_killed

    @staticmethod
    def GetFoesToKill():
        """
        Retrieve the number of foes to kill in the current map.
        Args: None
        Returns: int
        """
        return Map.map_instance().foes_to_kill

    @staticmethod
    def GetCampaign():
        """
        Retrieve the campaign of the current map.
        Args: None
        Returns: tuple (int, str)
        """
        campaign = Map.map_instance().campaign
        return campaign.ToInt(), campaign.GetName()

    @staticmethod
    def GetContinent():
        """
        Retrieve the continent of the current map.
        Args: None
        Returns: tuple (int, str)
        """
        continent = Map.map_instance().continent
        return continent.ToInt(), continent.GetName()

    @staticmethod
    def GetRegionType():
        """
        Retrieve the region type of the current map.
        Args: None
        Returns: tuple (int, str)
        """
        region_type = Map.map_instance().region_type
        return region_type.ToInt(), region_type.GetName()

    @staticmethod
    def GetDistrict():
        """Retrieve the district of the current map."""
        return Map.map_instance().district

    @staticmethod
    def GetRegion():
        """Retrieve the region of the current map."""
        region = Map.map_instance().server_region
        return region.ToInt(), region.GetName()

    @staticmethod
    def GetLanguage():
        """
        Retrieve the language of the current map.
        Args: None
        Returns: tuple (int, str)
        """
        language = Map.map_instance().language
        return language.ToInt(), language.GetName()

    @staticmethod
    def RegionFromDistrict(district):
        """
        Retrieve the region from a district.
        Args:
            district (int): The district to retrieve the region from.
        Returns: tuple (int, str)
        """
        region = Map.map_instance().RegionFromDistrict(district)
        return region.ToInt(), region.GetName()

    @staticmethod
    def LanguageFromDistrict(district):
        """
        Retrieve the language from a district.
        Args:
            district (int): The district to retrieve the language from.
        Returns: tuple (int, str)
        """
        language = Map.map_instance().LanguageFromDistrict(district)
        return language.ToInt(), language.GetName()

    @staticmethod
    def GetIsMapUnlocked(mapid=None):
        """Check if the map is unlocked."""
        if mapid is None:
            map_id = Map.GetMapID()
        else:
            map_id = mapid
        map_id_instance = PyMap.MapID(map_id)
        return map_id_instance.GetIsMapUnlocked(map_id_instance.map_id.ToInt())

    @staticmethod
    def GetAmountOfPlayersInInstance():
        """Retrieve the amount of players in the current instance."""
        return Map.map_instance().amount_of_players_in_instance
