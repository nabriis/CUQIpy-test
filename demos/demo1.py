# %% Demo 1
import sys; sys.path.append("..")
import package

package.class1()
package.class2()

print("Success")

# %%
from package.module1 import class1

class1()

print("Success")
# %%
