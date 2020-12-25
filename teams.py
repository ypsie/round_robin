import numpy as np
import pandas as pd 

class RoundRobin():

    def __init__(self,players,teams):
        
        self.player_list = players
        self.player_count, _ = self.player_list.shape
        self.teams = teams
        self.player_dict = {}
        self.games = 1

        if self.player_count%2 == 1:
            bye = np.array(['Bye-week'])
            self.player_list = np.concatenate((self.player_list, [bye]))
            self.player_count += 1
    
    def print_players(self):
        print(self.player_list)
        
    def generate_schedule(self):
        #Shuffle raus zum debuggen
        np.random.shuffle(self.player_list)
        flip_index = self.player_count//2 - 1
        players = self.player_list
        first = players[0]
        rest = players[1:]
        rest = np.concatenate((rest[:flip_index],np.flip(rest[flip_index:])))
        players = np.concatenate(([first], rest))
        self.schedule = np.reshape(players, (2, len(players)//2))
        
        
        ################################################################
        
        for _ in range(self.player_count - 2):

            rest = np.concatenate((rest[:flip_index],np.flip(rest[flip_index:])))
            #print(rest)
            rest = np.roll(rest,1)
            #print(rest)
            rest = np.concatenate((rest[:flip_index],np.flip(rest[flip_index:])))
            #print(rest)
            players = np.concatenate(([first], rest))
            games = np.reshape(players, (2, len(players)//2))
            #print(games)
            self.schedule = np.concatenate((self.schedule, games))
        
        ################################################################
        
    def stack_csv(self, teams_assigned=True):
        rows, cols = self.schedule.shape
        header = np.array([['Spieltag','Heimspieler','Heimmannschaft','Heimtore','Auswärtstore','Auswärtsmannschaft','Auswärtsspieler']])
        day = 0
        if teams_assigned:
            for x in range(2):
                for row in range(0,rows-1, 2):
                    day += 1 
                    for col in range(cols):
                        if x == 0:
                            
                            temp = np.array([day,self.schedule[row][col], self.team_schedule_hin[row][col], ' ', ' ', self.team_schedule_hin[row+1][col], self.schedule[row+1][col]])
                            header = np.concatenate((header,[temp]))
                            #hinrunde
                        elif x == 1:
                            temp = np.array([day, self.schedule[row+1][col], self.team_schedule_rueck[row+1][col],' ', ' ', self.team_schedule_rueck[row][col],self.schedule[row][col]])
                            header = np.concatenate((header,[temp]))

        self.csv_stack = header                            




    def write_csv(self):
        pd.DataFrame(self.csv_stack).to_csv("spielplan.csv",header=None,index=None)

    def print_schedule(self, teams_assigned=False):
        rows, cols = self.schedule.shape
        if not teams_assigned:
            for _ in range(2):
                for row in range(0,rows-1, 2):
                    print(f'------------------\nSpieltag\t{self.games}\n------------------\n')
                    for col in range(cols):
                        print(self.schedule[row][col], ' vs. ', self.schedule[row+1][col],'\n')
                    self.games +=1
        else:
            for _ in range(2):
                for row in range(0,rows-1, 2):
                    print(f'------------------\nSpieltag\t{self.games}\n------------------\n')
                    for col in range(cols):
                        if self.games > rows//2:
                            print(self.schedule[row][col], ' w. ', self.team_schedule_rueck[row][col], ' vs. ', self.schedule[row+1][col],' w. ', self.team_schedule_rueck[row+1][col], '\n')
                        else:
                            print(self.schedule[row][col], ' w. ', self.team_schedule_hin[row][col], ' vs. ', self.schedule[row+1][col],' w. ', self.team_schedule_hin[row+1][col], '\n')
                    self.games +=1


    def assign_teams_once(self):
        debug = 1
        rows, cols = self.schedule.shape
        team_schedule = [[' '*10 for _ in range(cols)] for _ in range(rows)]
        self.team_schedule_hin = np.array(team_schedule)
        self.team_schedule_rueck = np.array(team_schedule)
        for i in range(len(self.player_list)):
                    self.player_dict[self.player_list[i][0]] = self.teams
        
        for runde in range(2):
            if runde == 1:
                player_dict_second_half = self.player_dict.copy()

            done = False
            while not done:
                done = True
                for row in range(0,rows-1, 2):
                    team_list = self.teams
                    for col in range(cols): 
                        home_player = self.schedule[row][col]
                        intersect = np.intersect1d(team_list.flatten(),self.player_dict[home_player].flatten())
                        if intersect.size == 0:
                            print('Round:', runde, 'Debug:', debug)
                            debug += 1 
                            done = False
                            if runde == 0:
                                for i in range(len(self.player_list)):
                                    self.player_dict[self.player_list[i][0]] = self.teams
                            elif runde == 1:
                                self.player_dict = player_dict_second_half.copy()
                            continue
                        
                        pick_home = np.random.choice(intersect)
                        
                        if runde == 0:
                            self.team_schedule_hin[row][col] = pick_home
                        elif runde == 1:
                            self.team_schedule_rueck[row][col] = pick_home

                        team_list = np.delete(team_list, np.where(team_list == pick_home)[0])
                        self.player_dict[home_player]= np.delete(self.player_dict[home_player], np.where(self.player_dict[home_player] == pick_home)[0])

                        away_player = self.schedule[row+1][col]
                        intersect = np.intersect1d(team_list.flatten(),self.player_dict[away_player].flatten())
                        if intersect.size == 0:
                            done = False
                            print('Round:', runde, 'Debug:', debug)
                            debug += 1
                            if runde == 0:
                                for i in range(len(self.player_list)):
                                    self.player_dict[self.player_list[i][0]] = self.teams
                            elif runde == 1:
                                self.player_dict = player_dict_second_half.copy()
                            continue

                        pick_away = np.random.choice(intersect)

                        if runde == 0:
                            self.team_schedule_hin[row+1][col] = pick_away
                        elif runde == 1:
                            self.team_schedule_rueck[row+1][col] = pick_away


                        team_list = np.delete(team_list, np.where(team_list == pick_away)[0])
                        self.player_dict[away_player]= np.delete(self.player_dict[away_player], np.where(self.player_dict[away_player] == pick_away)[0])
                        


players = np.array([['Ringo'],['John'],['Paul'],['Yoko'],['George'],['Linda']])
teams = np.array([['Packers'],['Patriots'],['Vikings'],['Rams'],['49ers'],['Chiefs'],['Dolphins'],['Seahawks'],['Lions'],['Panthers']])

if __name__ == '__main__':
    turnier = RoundRobin(players=players, teams=teams)
    turnier.generate_schedule()
    

    turnier.assign_teams_once()
    turnier.print_schedule(True)
    turnier.stack_csv()
    turnier.write_csv()
    
    #print(turnier.schedule.shape)

