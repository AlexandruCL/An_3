// 1. A

public void printSomePoints(List<Point> points) {
 int printedPoints = 0;
 for (Point point : points) {
 if (someCondition()) {
 System.out.println(String.format("Point %d (%f,%f)",
printedPoints, point.getX(), point.getY()));
 }
 }
}
class Point {
 private double x;
 private double y;
 //getters and setters
}
