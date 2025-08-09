package com.example.mdmjive.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.example.mdmjive.database.dao.*
import com.example.mdmjive.database.entities.*

@Database(
    entities = [
        LogEntry::class,
        DeviceInfo::class,
        PolicyRecord::class,
        AuditRecord::class
    ],
    version = 1
)
abstract class LogDatabase : RoomDatabase() {
    abstract fun logDao(): LogDao
    abstract fun deviceDao(): DeviceDao
    abstract fun policyDao(): PolicyDao
    abstract fun auditDao(): AuditDao

    companion object {
        @Volatile
        private var INSTANCE: LogDatabase? = null

        fun getDatabase(context: Context): LogDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context,
                    LogDatabase::class.java,
                    "mdm_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}