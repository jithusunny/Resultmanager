from re import search, sub, findall
from urllib import urlopen
from stripogram import html2text

def prune(text):
    '''After pruning what we get is a [subject marks P/F] string'''
    text = sub(r'\n|\t', ' ', text)
    text = sub(r'.*Status|P : Passed.*', '', text)
    text = sub(r'[a-zA-Z]{2,}[0-9]{2,}', '', text)
    return sub(r' {2,}', ' ', text).strip()

def get_sub_list(text):
    '''Returns the list of subjects'''
    sub_list = []
    sub_line_match = search(r'[a-zA-Z -&/]+[0-9 ]*(P|F)', text)
    while sub_line_match:
        sub_line = sub_line_match.group()
        sub_match = search(r'([a-zA-Z -&/])+', sub_line)
        if sub_match:
            sub_list.append(sub_match.group().strip())
        text = text[len(sub_line):].strip()
        sub_line_match = search(r'[a-zA-Z -&/]+[0-9 ]*(P|F)', text)
    return sub_list

def no_result(string):
    '''Returns true if the particular string contains label 'withheld'/'Withheld'''
    return search(r'withheld|Withheld|invalid|not registered', string)

def main():
    
    url = 'http://202.88.252.6/exams/results1/btechNEW/btechresults_dis1.php?id=1393&regno=etaieec074&Submit=Submit'
    total_marks = 1100
    strength = 72

    sub_dict = {}
    total_failed = 0
    topper = [0] * 3
    perc_groups = [0] * 4
    effective_strength = strength
    
    roll_prefix = search(r'(?<=regno=)[a-zA-Z]+', url).group()
    url_prefix = search(r'.*?regno=', url).group()
    
    res_file = open(roll_prefix, 'w')
    
    html = urlopen(url).read()
    text = prune(html2text(html))
    sub_list = get_sub_list(text)

    for subject in sub_list:
        sub_dict[subject] = 0

    res_file.write('Roll number\tTotal\tPercentage')
    res_file.write( '\n----------- \t----- \t----------\n')

    for stud in range(1, strength + 1):
        try:
            stud_total = 0
            fail = False

            if stud < 10:
                roll = roll_prefix + '00' + str(stud)
            elif stud < 100:
                roll = roll_prefix + '0' + str(stud)
            else:
                roll = roll_prefix + str(stud)

            html = urlopen(url_prefix + roll + '&Submit=Submit').read()

            if no_result(html):
                effective_strength -= 1
                continue

            text = prune(html2text(html))

            for subject in sub_dict:
                sub_line = search(r'(?<=' + subject + ')'+ '[0-9 -A]+ [PF]', text).group().strip()
                sub_line = sub_line.split()

                if sub_line[-1] == 'F':
                    fail = True
                    sub_dict[subject] += 1
                    continue
                stud_total += int(sub_line[-2])

            if fail:
                total_failed += 1
            else:
                perc = float(stud_total)/total_marks * 100

                res_file.write(str(roll) + '\t ' + str(stud_total) + '\t  ' + '%.2f\n' %(perc))
                if perc >= 80:
                    perc_groups[0] += 1
                if perc >= 75:
                    perc_groups[1] += 1
                if perc >= 60 and perc < 75:
                    perc_groups[2] += 1
                if perc < 60:
                    perc_groups[3] += 1

                if stud_total > topper[1]:
                    topper[0], topper[1] = roll, stud_total
        except:
            pass

    res_file.write( '\nTopper of the class is:' + topper[0] + ' - Marks: ' + str(topper[1]) + ' Percentage: %.2f' %(float(topper[1])/total_marks * 100))
    res_file.write( '\n\nNo.of students with percentage above 80%: ' + str(perc_groups[0]))
    res_file.write( '\nNo.of students with percentage above 75%: ' + str(perc_groups[1]))
    res_file.write( '\nNo.of students with percentage in between 60% and 75%: ' + str(perc_groups[2]))
    res_file.write( '\nNo.of students with percentage below 60%: ' + str(perc_groups[3]))
    res_file.write( '\nClass Pass Percentage: %.4f(%d out of %d Students)\n' %(float(effective_strength-total_failed)/effective_strength*100, effective_strength-total_failed, effective_strength))

    for subject in sub_dict:
        res_file.write( '\nPass Percentage in ' + subject + " is: %.4f" %(float(effective_strength-sub_dict[subject])/effective_strength*100))
    res_file.write('\n')

if __name__ == '__main__':
    main()
