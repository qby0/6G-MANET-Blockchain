#ifndef NS3_SIMPLE_BLOCKCHAIN_H
#define NS3_SIMPLE_BLOCKCHAIN_H

#include "ns3/object.h"
#include "ns3/node.h"
#include "ns3/simulator.h"
#include "ns3/application.h"
#include <string>
#include <map>
#include <fstream>
#include <iostream>
#include <ctime>

namespace ns3 {

/**
 * \brief Simple blockchain integration for NS-3
 * Communicates with BlockSim via file-based IPC
 */
class SimpleBlockchain : public Object
{
public:
  /**
   * \brief Get the type ID
   */
  static TypeId GetTypeId (void);

  /**
   * \brief Constructor
   */
  SimpleBlockchain ();

  /**
   * \brief Destructor
   */
  virtual ~SimpleBlockchain ();

  /**
   * \brief Initialize blockchain with IPC directory
   * \param ipcDir Directory for file-based communication
   */
  void Initialize (const std::string& ipcDir = "ns3_blocksim_ipc");

  /**
   * \brief Send transaction to BlockSim
   * \param senderId Sender node ID
   * \param recipientId Recipient node ID
   * \param data Transaction data
   * \param txId Transaction ID (optional, will be generated if empty)
   * \return Transaction ID
   */
  std::string SendTransaction (uint32_t senderId, uint32_t recipientId, 
                              const std::string& data, 
                              const std::string& txId = "");

  /**
   * \brief Check if transaction is validated
   * \param txId Transaction ID
   * \return True if validated
   */
  bool IsTransactionValidated (const std::string& txId);

  /**
   * \brief Get transaction result
   * \param txId Transaction ID
   * \return JSON string with result or empty if not found
   */
  std::string GetTransactionResult (const std::string& txId);

  /**
   * \brief Read all new results from BlockSim
   * \return Number of new results processed
   */
  int ProcessBlockSimResults ();

  /**
   * \brief Get bridge status
   * \return True if bridge is active
   */
  bool IsBridgeActive ();

private:
  /**
   * \brief Generate unique transaction ID
   */
  std::string GenerateTransactionId ();

  /**
   * \brief Write transactions to file for BlockSim
   */
  void WriteTransactionsToFile ();

  /**
   * \brief Read current file content
   */
  std::string ReadFile (const std::string& filename);

  /**
   * \brief Write content to file
   */
  void WriteFile (const std::string& filename, const std::string& content);

  std::string m_ipcDir;                          ///< IPC directory path
  std::string m_ns3ToBlocksimFile;              ///< File for NS-3 -> BlockSim
  std::string m_blocksimToNs3File;              ///< File for BlockSim -> NS-3
  std::string m_statusFile;                     ///< Bridge status file
  
  std::map<std::string, std::string> m_pendingTransactions;  ///< Pending transactions
  std::map<std::string, std::string> m_validatedTransactions; ///< Validated transactions
  
  uint32_t m_transactionCounter;                ///< Transaction counter
  double m_lastResultCheck;                    ///< Last time we checked results
};

/**
 * \brief Simple blockchain application for testing
 */
class SimpleBlockchainApp : public Application
{
public:
  static TypeId GetTypeId (void);

  SimpleBlockchainApp ();
  virtual ~SimpleBlockchainApp ();

  /**
   * \brief Set blockchain instance
   */
  void SetBlockchain (Ptr<SimpleBlockchain> blockchain);

  /**
   * \brief Send a test transaction
   */
  void SendTestTransaction (uint32_t recipientId, const std::string& data);

protected:
  virtual void StartApplication (void);
  virtual void StopApplication (void);

private:
  /**
   * \brief Periodic function to check blockchain results
   */
  void CheckBlockchainResults ();

  Ptr<SimpleBlockchain> m_blockchain;
  EventId m_checkEvent;
  Time m_checkInterval;
  uint32_t m_testCounter;
};

} // namespace ns3

#endif /* NS3_SIMPLE_BLOCKCHAIN_H */ 