def append_col(df1, df2, append_colname, index_colname1, index_colname2, new_colname):
    '''Appends append_colname from df2 to df1 with new_colname as name; compares the values in index_colname1 and
    index_colname2 to decide where to add which values. Adds None if it cant find a value index_colname1 in
    index_colname2'''

    append_list = []

    for value in df1[index_colname1].values.tolist():

        try:
            append_list.append(df2[df2[index_colname2] == value][append_colname].values[0])
        except IndexError:
            append_list.append(None)

    df1[new_colname] = append_list

    print(append_colname + ' appended as ' + new_colname)
