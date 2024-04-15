def match(hashes, dictionaries, miss_lim = 2, match_at = 5):
    #dict = {
    #        "incidentName": newIncidentName,
    #        "fingerprints": [[hashes],[hashes]]
    #        }

    for dictionary in dictionaries: 
        incident = dictionary["incidentName"]
        audios = dictionary["fingerprints"]
        
        # check with start of audio in db is part way through the audio
        for k in range(len(audios)):
            hash_set = audios[k]
            for i in range(len(hashes)):
                for j in range(len(hash_set)):
                    curr = 0
                    tot = 0
                    misses = 0
                    itemp = i
                    jtemp = j
                    while itemp in range(len(hashes)) and jtemp in range(len(hash_set)) and misses < miss_lim:
                        
                        if hashes[itemp] == hash_set[jtemp]:
                            curr +=1
                            
                            if (curr == match_at):
                                print("matched to incident ", incident)
                                return incident, dictionary
                        else:
                            misses +=1
                        tot +=1
                        itemp +=1
                        jtemp +=1
             
        # check with start of audio is part way through the audio in the db
        for k in range(len(audios)):
            hash_set = audios[k]
            for j in range(len(hash_set)):
                for i in range(len(hashes)):
                    curr = 0
                    tot = 0
                    misses = 0
                    itemp = i
                    jtemp = j
                    while itemp in range(len(hashes)) and jtemp in range(len(hash_set)) and misses < miss_lim:
                        if hashes[itemp] == hash_set[jtemp]:
                            curr +=1
                            if (curr == match_at):
                                print("matched to incident ", incident, 'at ', itemp, '/', len(hashes), jtemp, len(hash_set))
                                return incident, dictionary
                        else:
                            misses +=1
                        tot +=1
                        itemp +=1
                        jtemp +=1   
                                                              
    print("no match")
    return len(dictionaries)+1, None