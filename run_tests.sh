export PYTHONPATH=:/Users/pnedoma/Dropbox/projects/hellog:.
for testfile in test/*.test.py
do
    python $testfile
done

