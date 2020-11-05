class User:

    def __init__(self, nickname, distance, pokemon, pokestops, experience):
        self.nickname = nickname
        self.distance = distance
        self.pokemon = pokemon
        self.pokestops = pokestops
        self.experience = experience

    def check_Distance(self):
        pass

    def print_User(self):
        print("Usuario ", self.nickname, "\n")
        print("\t Distance ", self.distance, "\n")
        print("\t Pokémon ", self.pokemon, "\n")
        print("\t Pokéstops ", self.pokestops, "\n")
        print("\t Experience ", self.experience, "\n")
