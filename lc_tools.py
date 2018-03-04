import pandas as pd
import numpy as np

def canvas_format(lcfile=None,cfile=None,score_method=None,write_file=None, **kwargs):
  """
  Transforms a Learning Catalytics gradebook into an importable format for Canvas.
  
  Parameters
  ----------
  lcfile : string
    filename of Learning Catalytics gradebook

  cfile : string
    filename of exported Canvas gradebook

  score_method : string {'SumSessions','SumPoints'}
    Either award a point per session joined (includes zeros, but not nulls),
    or sum points across all columns. Default is 'SumSessions'

  write_file : string 
    Name of output .csv file
    
  Examples
  --------
  
    >>> lc_to_canvas.format(lcfile='LC_grades.csv',cfile='CanvasExport.csv',score_method='SumSessions', write_file='LC_grades_canvas.csv')

    Can be run as a script:
    $ python lc_to_canvas.py lcfile='LC_grades.csv',cfile='CanvasExport.csv',score_method='SumSessions', write_file='LC_grades_canvas.csv'

  Returns
  -------
    merged_df : Pandas Dataframe
      Merged Learning Catalytics/Canvas data frame

      merged_df is written to a .csv file that is importable to Canvas
    
  """
  
  #Set default write_file
  if write_file==None: write_file='lc_canvas_output.csv'
  print('---->Output will be written to '+write_file)
  
  #How should the LC columns be scored?
  if score_method==None: score_method='SumSessions'
  print('---->Scores are calculated as '+score_method)
   
  #Use Pandas to read .csv files into data frames
  lcdata=pd.read_csv(lcfile, sep=',')
  cdata=pd.read_csv(cfile, sep=',')

  #Get a list of all column names, and a smaller list with just the LC scores (beyond 4th column)
  allcols = [col for col in lcdata]
  cols = [col for col in lcdata.iloc[:,4::]]
  print('---->Learning Catalytics Assignment List:')
  print(cols)

  #Combine student names from LC gradebook into Canvas Format
  lastname=lcdata['Last name']
  firstname=lcdata['First name']
  students=firstname+' '+lastname

  if score_method=='SumSessions':
    #Convert a ~NaN into a single point for each LC session
    #(We are counting attendance, not the number of Qs answered correctly)
    lcdata[cols]=~np.isnan(lcdata[cols])*1
    
  #Determine the total number of LC sesssions scored, and total number of points
  num_sessions=len(cols)
  total_points=(lcdata[cols].max(axis=0)).sum(axis=0)
  print('---->The Learning Catalytics gradebook has '+str(num_sessions)+' total sessions')
  print('---->The Learning Catalytics gradebook has '+str(total_points)+' total points')

  
  #Sum the number of LC sessions or points for each student
  lctotal=lcdata[cols[:]].sum(axis=1)
  if score_method=='SumSessions':
    (lctotal[lctotal > num_sessions])=num_sessions #Students cannot have score > num_sessions

  #Create a new column with student names in Canvas format
  lcdata['Student']=pd.Series(students,index=lcdata.index)

  #Create a new column for the summmed totals, named for the Canvas Gradbook column
  lcdata['LC score']=pd.Series(lctotal,index=lcdata.index)

  #Search for duplicates and keep last entry (will have to manually check LC gradebook for these)
  duplicate=lcdata.duplicated(subset='Student', keep='last')
  if len(students[duplicate]) > 0:
    print('---->Duplicate Entires in LC Gradebook:')
    print(students[duplicate])
    print('---->Deleting all but last duplicate')
  #Delete duplicate rows
  lcdata.drop(lcdata.index[duplicate])

  #Delete all original columns in lcdata, leaving us with only the two new columns we created
  for item in allcols:
    del lcdata[item]

  #Grab mandatory columns needed for import from Canvas gradebook
  canvascols = [col for col in cdata if col in ['Student','ID','SIS User ID','SIS Login ID','Section']]

  #Grab junk columns (everything else) from Canvas gradebook
  junkcols = [col for col in cdata if col not in ['Student','ID','SIS User ID','SIS Login ID','Section']]

  #Delete the junk columns
  for item in junkcols:
    del cdata[item]
  
  #Canvas wants a line in the 'Student' Field for Points Possible
  #so we will add this "student" to the LC gradebook
  #index=[0] indicates we want this line as the first entry in our data frame
  if score_method=='SumSessions':
    newline_lc = pd.DataFrame({'Student': '    Points Possible', 'LC score': num_sessions}, index=[0])

  if score_method=='SumPoints':
    newline_lc = pd.DataFrame({'Student': '    Points Possible', 'LC score': total_points}, index=[0])
    
  #Concatenate the new lines to our existing dataframe
  lcdata = pd.concat([newline_lc,lcdata.iloc[:]]).reset_index(drop=True)

  #Merge LC and Mastering dataframes
  df=pd.merge(cdata,lcdata,how='outer', on='Student')

  #Write data frames to .csv file
  df.to_csv(path_or_buf=write_file,index=False)

  return df

if __name__ == "__main__":
    import sys
    kwargs=dict(arg.split('=') for arg in sys.argv[1:])

    #check for mandatory kwargs
    mandatory=['lcfile','cfile']
    for item in mandatory:
      if item not in kwargs:
        raise SyntaxError('Missing keyword argument: '+item)

    #function call with kwargs
    canvas_format(**dict(arg.split('=') for arg in sys.argv[1:]))
