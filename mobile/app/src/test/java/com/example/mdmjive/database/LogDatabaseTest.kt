package com.example.mdmjive.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.mdmjive.database.entities.AuditRecord
import com.example.mdmjive.database.entities.DeviceInfo
import com.example.mdmjive.database.entities.LogEntry
import com.example.mdmjive.database.entities.PolicyRecord
import org.junit.After
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class LogDatabaseTest {

    private val context = ApplicationProvider.getApplicationContext<Context>()

    @After
    fun tearDown() {
        context.deleteDatabase("mdm_database")
    }

    @Test
    fun createsDatabase() {
        val db = LogDatabase.getDatabase(context)
        assertTrue(db.isOpen)
        db.close()
    }

    @Test
    fun fallbackToDestructiveMigrationAllowsUpgrade() {
        val db = LogDatabase.getDatabase(context)
        db.close()

        val upgradedDb = Room.databaseBuilder(
            context,
            LogDatabaseV2::class.java,
            "mdm_database"
        ).fallbackToDestructiveMigration().build()
        assertTrue(upgradedDb.isOpen)
        upgradedDb.close()
    }
}

@Database(
    entities = [
        LogEntry::class,
        DeviceInfo::class,
        PolicyRecord::class,
        AuditRecord::class
    ],
    version = 2
)
abstract class LogDatabaseV2 : RoomDatabase()
