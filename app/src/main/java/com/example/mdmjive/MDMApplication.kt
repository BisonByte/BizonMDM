import android.app.Application
import com.example.mdmjive.database.LogDatabase
import timber.log.Timber

class MDMApplication : Application() {
    lateinit var database: LogDatabase

    override fun onCreate() {
        super.onCreate()

        // Inicializamos la base de datos
        database = LogDatabase.getDatabase(applicationContext)

        // Plantamos Timber para logging
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }
    }
}
