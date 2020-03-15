pragma solidity ^0.5.0;

import "./Registration.sol";

contract Project {
  
    Registration registrationContract;

    constructor(Registration registrationAddress) public {
        registrationContract = registrationAddress;
    }
    
    enum projectState { pending, approved, rejected }
    address _owner = msg.sender;
    
    struct CharityProject {
        uint256 projectOrganizationId;
        uint256 projectOwnerId; 
        uint256 beneficiaryListId;
        uint256 projectDocumentationId; 
        
        uint256 inspectorId;
        uint256 beneficiaryGainedRatio;
        
        projectState state; 
        uint256 numOfDonationReceived; 
        uint256 amountOfDonationReceived; 
        uint256 amountOfDonationBeneficiaryReceived; 
    }
    
    // struct Inspector {
    //     address inspectorAddress; 
    // }
    
    struct Check {
        uint256 projectId;
        uint256 inspectorId; 
        projectState state; 
        string reason; 
    }
    
    // mapping(uint256 => Inspector) inspectorList;
    mapping(uint256 => Check) checkingList; 
    mapping(uint256 => uint256) projectCheckingDetails; 
    mapping(uint256 => CharityProject) projectList; 
    
    // uint256 numInspectors; 
    uint256 numProjects; 
    uint256 numChecks; 
    
    // function registerInspector(address inspectorAddress) public payable onlyOwner returns (uint256){
        
    //     Inspector memory newInspector = Inspector(inspectorAddress); 
    //     uint256 newInspectorId = numInspectors++;
    //     inspectorList[newInspectorId] = newInspector; 
        
    //     return newInspectorId; 
    // }
    
    function registerProject(uint256 organizationId, uint256 ownerId, uint256 beneficiaryListId, uint256 documentationId, uint256 beneficiaryGainedRatio) public payable returns (uint256){
        uint256 numberOfInspectors = registrationContract.getNumOfInspectors();
        CharityProject memory newProject = CharityProject(
            organizationId, 
            ownerId,
            beneficiaryListId, 
            documentationId,
            (uint256)(block.timestamp % numberOfInspectors) + 1, // random number generate assigned inspectorId 
            beneficiaryGainedRatio,
            projectState.pending, 
            0,
            0,
            0
        );
        uint256 newProjectId = numProjects++; 
        projectList[newProjectId] = newProject; 
        
        Check memory newCheck = Check(
            newProjectId,
            newProject.inspectorId,
            projectState.pending,
            'null'
        );
        uint256 newCheckId = numChecks++; 
        checkingList[newCheckId] = newCheck; 
        projectCheckingDetails[newProjectId] = newCheckId;
        
        return newProjectId; 
    }
    
    // function distributeDonation(uint256 donationAmount, uint256 projectId) public{
    //     projectList[projectId].numOfDonationReceived = projectList[projectId].numOfDonationReceived + 1;
    //     projectList[projectId].amountOfDonationReceived += donationAmount;
    //     projectList[projectId].amountOfDonationBeneficiaryReceived += donationAmount * projectList[projectId].beneficiaryGainedRatio;
    // }
    
    function approveProject(uint256 projectId) public onlyAppointedInspector(projectId) {
        require(
            projectList[projectId].state == projectState.pending,
            "Cannot deal with accepted or rejected projects"
        );
        
        projectList[projectId].state = projectState.approved;
        
        uint256 checkId = projectCheckingDetails[projectId];
        checkingList[checkId].state = projectState.approved;
        // checkingList[checkId].reason = approveReason;
    }
    
    function rejectProject(uint256 projectId) public onlyAppointedInspector(projectId) {
        require(
            projectList[projectId].state == projectState.pending,
            "Cannot deal with accepted or rejected projects"
        );
        
        projectList[projectId].state = projectState.rejected;
        
        uint256 checkId = projectCheckingDetails[projectId];
        checkingList[checkId].state = projectState.rejected;
        // checkingList[checkId].reason = rejectReason;
    }
    
    modifier onlyAppointedInspector(uint256 projectId) {
        // require(msg.sender == inspectorList[projectList[projectId].inspectorId].inspectorAddress, "Invalid inspector");
        address appointedInspectorAddress = registrationContract.getInspectorAddressById(projectList[projectId].inspectorId); 
        
        require(msg.sender == appointedInspectorAddress, "Invalid inspector");
        _;
    }
    
    modifier onlyOwner() {
        require(msg.sender == _owner, "Invalid owner");
        _;
    }
}