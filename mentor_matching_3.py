#This file contains the stable matching algorithm used to match mentees with mentors in India.

#Score Function:
#For similarity function f, we will compute the absolute difference between two respondents for each answer and sum all those differences up.
#We will then compare the difference sum with the average of the two respondent's similar function values, and if they match or are close, this is a good pairing.
#For instance, an average f value of 0.5 and a difference sum value of 20/40 would be a good match. An average f value of 0.1 would be aligned with a difference sum of 36.
#We connect the class year with the similarity computation
import json
import os
import glob
import pandas as pd

from math import radians, degrees, sin, cos, asin, acos, sqrt
import operator

with open("mentees.json") as f:
	mentee_data = json.load(f)

f.close()

with open("mentors.json") as f:
    mentor_pre_data = json.load(f)
f.close()

mentor_data = {}
counter = 0
for i in mentor_pre_data.keys():
    for j in range(mentor_pre_data[i]["num_mentees"]):
        mentor_data[str(counter)] = mentor_pre_data[i]
        counter +=1
num_mentees = len(mentee_data)
num_mentors = len(mentor_data)


def score(a, b):	#a represents a number from 0 to the total # of mentees. b represents a number from 0 to the total # of mentors.
	a_topic_preferences = mentee_data[a]["topic_preferences"]
	#a_grade = mentee_data[a]["grade"]
	a_personality = mentee_data[a]['personality']
	#a_city = mentee_data[a]["city"]
	a_gender_pref = mentee_data[a]["gender_pref"]
	a_languages = mentee_data[a]["languages"]

	b_expertise = mentor_data[b]["expertise"]
	b_personality_pref = mentor_data[b]["personality_pref"]
	b_gender = mentor_data[b]["gender"]
	#b_city = mentor_data[b]["city"]
	b_languages = mentor_data[b]["languages"]

	topic_match_counter = 0
	for i in range(len(a_topic_preferences)):
		for j in range(len(b_expertise)):
			#if the expertise of the mentor and topic preference of the mentee does not match up, automatically incompatible
			if a_topic_preferences[i] == b_expertise[j]:
				topic_match_counter += 1
	if topic_match_counter == 0:
		return 0

	language_match_counter = 0
	for i in range(len(a_languages)):
		for j in range(len(b_languages)):
			if a_languages[i] == b_languages[j]:
				language_match_counter +=1

	if not (b_gender == "Any" or b_gender == a_gender_pref):
		return 0

	diff_personality = 0	#how different is the personality of the mentee compared with the personality preference of the mentor?
	for i in range(6):
		diff_personality += abs(b_personality_pref[i] - a_personality[i])	#max difference is 20, min difference is 0. 20 means completely different, 0 means fully aligned.


	# Smaller distance -> better (larger) score. Largest possible distance within india is around 3500km.
	# Smaller difference between a mentee's personality and a mentor's preference for their mentee's personality -> better (larger) score.
	overall_score = 4000 - (diff_personality) * 50 + (topic_match_counter - 1) * 500 + 300 * (language_match_counter - 1)
	return overall_score

#In contrast to gale_shapley in the context of university admissions, each mentor will have their own holding space for a mentee.
#This space contains a dictionary index in "mentees" from 0 to 3 which indicates which mentee is currently assigned to them, as well as the respective mutual score value.
#This space is interchangeable and mentees can be replaced if this contributes to a more stable arrangement.
#For each mentee, compute the score value between the mentee and all mentors. Take the pairing with the highest score value and place the mentee into the mentor's space.
#As we repeat this process for each mentee, we will check if the favourite mentor's space is empty. If not, compare the score values of current mentee with mentee in space.
#Replace the mentee in mentor's place with the current mentee if the current mentee's compatibility score is higher.
#Have a list of mentees who will be "shooting their shot" the next round. Remove new mentee in a mentor's space from this list. Add displaced mentees back into proposing list.
#Have a list of mentee_ids in each mentor_space key value pair where each one can search whether or not a particular mentee has already visited the mentor or not. If the mentee
#has already visited the mentor and the mentor's slot is not empty, then the guy ignores the that mentor and moves on because the mentee knows that he or she cannot get the mentor. im)
#If the mentee visited before and is not in that mentor's slot now, that means someone more compatible replaced him or her.
#The mentee can never be "better" than someone that is better than him or her with respect to a specific mentor, so move on. Otherwise the mentee will never find a match.
#Iterate through this process until every single mentee and mentor have a pairing: everyone should be in a pair at the end of the algorithm.

def gale_shapley():
	proposing = []	#list of proposing mentees while mentor slots = []
	for x in range(num_mentees):    #4 is the size of the mentees at the moment, but we need to change this as it is fixed.
		proposing.append(x)

	high_scores = []	#corresponding high scores with each mentee
	for y in range(num_mentees):
		high_scores.append(0)

	current_favorite = []	#list of each mentee's current favorite mentor
	for z in range(num_mentees):
		current_favorite.append(-1)
	#the above lists all match element for element (for any i, proposing[i] has current highest score value high_scores[i] with current_favorite[i])

	prop_tracker = []
	mentor_space = {}
	for d in range(num_mentors):
		mentor_space[d] = {'mentee_id': -5, 'favorite_score': -1, 'mentees_visited': []}
	temp = 0
	while temp == 0:
		prop_tracker = list(proposing)
		for i in range(num_mentees):	#each mentee
			if proposing[i] < 0:
				pass
			else:
				high_score = -1
				for k in range(num_mentors):	#each mentor
					if i in mentor_space[k]["mentees_visited"]:
						#skip this mentor and move onto scoring compatibility with next mentor in the list
						pass
					else:
						if high_score < score(str(i), str(k)):
							high_score = score(str(i), str(k))
							high_scores[i] = high_score		#update highest score value corresponding to current mentee
							current_favorite[i] = k 	#connect highest score value mentor with current mentee

		#By now, our list of proposing mentees have been initialized, as well as their respective high scores and which mentor they had the highest score with.

		#girl_slot = {'mentee_id': -5, 'favorite_score': -1, 'mentees_visited': []}  #each space contains the mentee's profile key and score value with mentor who owns the space
		for j in range(num_mentors):
			for b in range(num_mentees):	#iterate through all mentee favorites to check for matches with current mentor
				if b not in mentor_space[j]["mentees_visited"] and proposing[b] != -1:
					if current_favorite[b] == j:	#if current mentor is a favorite of a mentee, update mentor space accordingly
						if mentor_space[j]['mentee_id'] == -5:	#if mentor space is empty
							mentor_space[j]['mentee_id'] = b
							mentor_space[j]['favorite_score'] = high_scores[b]
							mentor_space[j]['mentees_visited'].append(b)
							proposing[b] = -1
							current_favorite[b] = -1
							high_scores[b] = -1
						else:
							if high_scores[b] > mentor_space[j]['favorite_score']:
								proposing[mentor_space[j]['mentee_id']] = mentor_space[j]['mentee_id']	#add mentee in slot back to proposing list
								mentor_space[j]['mentee_id'] = b	#update slot with new, more compatible mentee
								mentor_space[j]['favorite_score'] = high_scores[b]
								mentor_space[j]['mentees_visited'].append(b)
								proposing[b] = -1	#new mentee not proposing to other mentors next round
								current_favorite[b] = -1
								high_scores[b] = -1
							else:
								mentor_space[j]['mentees_visited'].append(b)
		full_counter = 0
		for c in range(len(mentor_space)):
			if mentor_space[c]['mentee_id'] == -5:
				full_counter += 1

		if full_counter <= max(0,num_mentors-num_mentees): #If either every mentee is taken care of OR every mentor is full, we're done.
			break

	return mentor_space

def stable():
	supposedly_stable = gale_shapley()
	counter = 0
	for i in range(num_mentees):
		for j in range(num_mentors):
			temp = score(str(i), str(j ))
			mentor_id = 0
			for k in supposedly_stable.keys():
				if supposedly_stable[k]['mentee_id'] == i:
					mentor_id = k
			if temp > supposedly_stable[j]['favorite_score'] and temp > supposedly_stable[mentor_id]['favorite_score']:
				counter += 1
	if counter == 0:
		return 1
	else:
		return 0

print(gale_shapley())
print(stable())
