import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import org.bson.Document;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.ScanRequest;

public class Store {
    private MongoCollection<Document> orders;
    private DynamoDbClient dynamo;

    public void all() {
        orders.find();
        orders.deleteMany(new Document());
        dynamo.scan(ScanRequest.builder().tableName("orders").build());
        dynamo.scan(ScanRequest.builder().tableName("orders").limit(10).build());
    }
}
