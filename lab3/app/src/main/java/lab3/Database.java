package lab3;

import spark.Request;
import spark.Response;
import com.google.gson.*;

import java.sql.*;
import java.util.*;

/**
 * Database is an interface to the college application database, it
 * uses JDBC to connect to a SQLite3 file.
 */
public class Database {

    /**
     * The database connection.
     */
    private Connection conn;
    private Gson gson = new Gson();

    /**
     * Creates the database interface object. Connection to the
     * database is performed later.
     */
    public Database() {
        conn = null;
    }

    /**
     * Opens a connection to the database, using the specified
     * filename (if we'd used a traditional DBMS, such as PostgreSQL
     * or MariaDB, we would have specified username and password
     * instead).
     */
    public boolean openConnection(String filename) {
        try {
            conn = DriverManager.getConnection("jdbc:sqlite:" + filename);
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
        return true;
    }

    /**
     * Closes the connection to the database.
     */
    public void closeConnection() {
        try {
            if (conn != null) {
                conn.close();
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    /**
     * Checks if the connection to the database has been established
     * 
     * @return true if the connection has been established
     */
    public boolean isConnected() {
        return conn != null;
    }

    /* ================================== */
    /* --- insert your own code below --- */
    /* ===============================*== */

}
