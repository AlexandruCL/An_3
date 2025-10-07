import java.util.*;

public class StudentRepository {
    private Collection<Student> students;

    public StudentRepository(Collection<Student> students) {
        this.students = new ArrayList<>(students);
    }

    public List<String> getStudentEmailsSortedByAgeUnderTheAgeOf(int age) {
        return null;
    }

    /**
     * @return returns the sorted list of distinct names.
     *
     * SIDE EFFECT: makes all student names uppercase
     */
    public List<String> makeStudentNamesUppercaseAndReturnThemAsSortedDistinctList() {
        return null;
    }

    public Set<String> getNonNullUniversities() {
        return null;
    }

    public Map<String, Student> getStudentsMappedByEmail() {
        return null;
    }

    public Map<String, List<Student>> getOverageStudentsGroupedByUniversity() {
        return null;
    }

    public Optional<Student> getTheStudentWithTheNthShortestEmail(int n) {
        return Optional.empty();
    }

    public Optional<String> getTheNameOfTheSecondOldestStudent() {
        return Optional.empty();
    }

    public OptionalDouble getAverageAgeOfNStudentsInUniversity(int n, String university) {
        return OptionalDouble.empty();
    }

    public long countStudentsWithNamesLongerThan(int n) {
        return -1;
    }

    /**
     * Students in no university (university == null) are considered to be in the same university
     */
    public long countNumberOfStudentsWithAtLeastNColleaguesInDifferentUniversity(int n) {
        return -1;
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
        return null;
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
