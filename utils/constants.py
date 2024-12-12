from enum import Enum

Role = Enum('Role', 
            [('GENERAL', None), 
             ('ITEM_OWNER', "ItemOwner"), 
             ('SECRETARIAT', "Secretariat")])

Item_Status = Enum('Item_Status', 
                   [('PENDING', "Pending"), 
                    ('WAITLIST', "Waitlist"), 
                    ('REGISTERED', "Registered"), 
                    ('REJECTED', "REJECTED")])
