# lc_tools
Tools to convert a Learning Catalytics gradebook into Canvas format.
Merges an LC gradebook with mandatory columns from a Canvas gradebook.

Can be called as a function within python:
> import lc_tools

> merged_gradebook = lc_tools.canvas_format(lcfile='lc_gradebook.csv', cfile='canvas_gradebook.csv',score_method='SumSessions',write_file='new_gradebook.csv')

Or from the command line:
> python lc_tools.py lcfile='lc_gradebook.csv' cfile='canvas_gradebook.csv' score_method='SumSessions' write_file='new_gradebook.csv'

In both of the above examples, the merged gradebook is written to a Canvas-importable .csv file.
