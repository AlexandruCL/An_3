import java.util.*;
import java.util.stream.Collectors;

public class StudentRepository {
    private Collection<Student> students;

    public StudentRepository(Collection<Student> students) {
        this.students = new ArrayList<>(students);
    }

    public List<String> getStudentEmailsSortedByAgeUnderTheAgeOf(int age) {
        return students.stream()
                .filter(student -> student.getAge() < age)
                .sorted(Comparator.comparingInt(Student::getAge))
                .map(Student::getEmail)
                .toList();
    }

    /**
     * @return returns the sorted list of distinct names.
     *
     * SIDE EFFECT: makes all student names uppercase
     */
    public List<String> makeStudentNamesUppercaseAndReturnThemAsSortedDistinctList() {
        students.forEach(s -> s.setName(s.getName().toUpperCase()));
        return students.stream()
            .map(Student::getName)
            .distinct()
            .sorted()
            .toList();
    }

    public Set<String> getNonNullUniversities() {
        return students.stream()
            .map(Student::getUniversity)
            .filter(Objects::nonNull)
            .collect(Collectors.toSet());
    }

    public Map<String, Student> getStudentsMappedByEmail() {
        return students.stream()
            .collect(Collectors.toMap(Student::getEmail, s -> s));
    }

    public Map<String, List<Student>> getOverageStudentsGroupedByUniversity() {
        return students.stream()
            .filter(s -> s.getAge() >= 18 && s.getUniversity() != null)
            .collect(Collectors.groupingBy(Student::getUniversity));
    }

    public Optional<Student> getTheStudentWithTheNthShortestEmail(int n) {
        return students.stream()
            .filter(s -> s.getEmail() != null)
            .sorted(Comparator.comparing(s -> s.getEmail().length()))
            .skip(n-1)
            .findFirst();
    }

    public Optional<String> getTheNameOfTheSecondOldestStudent() {
        return students.stream()
            .sorted(Comparator.comparingInt(Student::getAge).reversed())
            .skip(1)
            .map(Student::getName)
            .findFirst();

    }

    public OptionalDouble getAverageAgeOfNStudentsInUniversity(int n, String university) {
        return students.stream()   
            .filter(s -> Objects.equals(s.getUniversity(), university))
            .limit(n)
            .mapToInt(Student::getAge)
            .average();
    }

    public long countStudentsWithNamesLongerThan(int n) {
        return students.stream()
            .filter(s -> s.getName() != null && s.getName().length() > n)
            .count();
    }

    /**
     * Students in no university (university == null) are considered to be in the same university
     */
    public long countNumberOfStudentsWithAtLeastNColleaguesInDifferentUniversity(int n) {
        return students.stream()
            .filter(student -> student.getColleagues().stream()
                        .filter(c -> !isInUniversity(student, c.getUniversity()))
                        .count() >= n
            )
            .count();
    }

    /**
     * Helper method for implementing countNumberOfStudentsWithAtLeastNColleaguesInDifferentUniversity(int n)
     */
    private static boolean isInUniversity(Student student, String university) {
        if (university == null)
            return student.getUniversity() == null;
        return university.equals(student.getUniversity());
    }

    public List<Student> getStudentsWithAtLeastOneColleagueWithSameEmailDomain() {
        return students.stream()
            .filter(s -> s.getEmail() != null)
            .filter(s -> s.getColleagues().stream()
                        .anyMatch(c -> c.getEmail() != null &&
                                 getEmailDomain(c.getEmail()).equals(getEmailDomain(s.getEmail()))
                        )
            )
            .distinct()
            .toList();
    }


    /**
     * Helper method for implementing getStudentsWithAtLeastOneColleagueWithDifferentEmailDomain()
     */
    private static String getEmailDomain(String email) {
        if(email.indexOf('@') == -1) {
            return "";
        }
        return email.substring(email.indexOf('@') + 1);
    }
}
