package lab3;

import static spark.Spark.*;

public class App {

    public static void main(String[] args) {
        new App().run();
    }

    private Database db = new Database();

    void run() {
        port(7007);
        // db.openConnection("lab3.sqlite");
        get("/ping", (req, res) -> "pong");
    }
}
