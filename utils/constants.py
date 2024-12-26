from enum import Enum

Role = Enum('Role', 
            [('GENERAL', None),
             ('PERSONAL_ASSISTANT', "Personal Assistant"),
             ('ITEM_OWNER', "ItemOwner"), 
             ('SECRETARIAT', "Secretariat")])

Item_Status = Enum('Item_Status', 
                   [('PENDING', "Pending"), 
                    ('WAITLIST', "Waitlist"), 
                    ('REGISTERED', "Registered"), 
                    ('CONFIRMED', "Confirmed"),
                    ('REJECTED', "REJECTED")])

Meeting_Status = Enum('Meeting_Status', 
                   [('CURATION', "Curation"), 
                    ('REVIEW', "Reviewing"), 
                    ('APPROVED_BY_COS', "Approved (COS)"), 
                    ('APPROVED_BY_HEAD', "Approved (Head)"),
                    ('CIRCULATED', "Circulated"),
                    ("COMPLETED", "Completed"),
                    ('REJECTED', "Rejected")])

Purpose_Lookup = Enum('Purpose_Lookup',
                      [("APPROVAL", "Tier 1 (For Approval)"),
                       ("DISCUSSION", "Tier 1 (For Discussion)"),
                       ("INFO", "Tier 2 (For Information)")])