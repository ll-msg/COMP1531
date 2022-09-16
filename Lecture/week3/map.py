def shout(string):
    return string.upper() + "!!!!"

if __name__ == '__main__':
    tutors = ['Simon', 'Teresa', 'Kaiqi', 'Michelle']
    # angry_tutors = list(map(lambda t: t.upper() + "!!!!", tutors))
    angry_tutors = []
    for tutor in tutors:
        angry_tutors.append(shout(tutor))
    print(angry_tutors)