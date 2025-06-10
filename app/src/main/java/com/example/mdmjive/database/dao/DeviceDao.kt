package com.example.mdmjive.database.dao

import androidx.room.*
import com.example.mdmjive.database.entities.DeviceInfo
import kotlinx.coroutines.flow.Flow

@Dao
interface DeviceDao {
    @Query("SELECT * FROM devices")
    fun getAllDevices(): Flow<List<DeviceInfo>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertDevice(device: DeviceInfo)

    @Query("SELECT * FROM devices WHERE deviceId = :deviceId")
    suspend fun getDevice(deviceId: String): DeviceInfo?
    abstract fun insert(deviceInfo: DeviceInfo)
}