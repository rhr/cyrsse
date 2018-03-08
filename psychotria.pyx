import newick
root = newick.parse(open('psychotria.newick').read())

areas = list('KOMH')

states = ['K', 'KO', 'O', 'OM', 'M', 'MH', 'H']
    
