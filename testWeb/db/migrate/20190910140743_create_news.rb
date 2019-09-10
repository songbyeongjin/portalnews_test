class CreateNews < ActiveRecord::Migration[6.0]
  def change
    create_table :news do |t|
      t.string :title
      t.text :content
      t.string :press
      t.string :writer
      t.datetime :date
      t.text :url
      t.string :portal

      t.timestamps
    end
  end
end
