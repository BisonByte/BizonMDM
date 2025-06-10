import android.app.Application
import androidx.room.Room
import com.example.mdmjive.database.DeviceDatabase
import timber.log.Timber

class MDMApplication : Application() {
    lateinit var database: DeviceDatabase

    override fun onCreate() {
        super.onCreate()

        // Inicializamos la base de datos
        database = Room.databaseBuilder(
            applicationContext,
            DeviceDatabase::class.java,
            "device_database"
        ).build()

        // Plantamos Timber para logging
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }
    }
}
